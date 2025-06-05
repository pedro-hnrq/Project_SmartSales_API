from datetime import datetime
from http import HTTPStatus
from typing import List, Optional, Tuple

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from smartsales.models.auth import UserRole
from smartsales.models.clients import Client
from smartsales.models.orders import Order, OrderItem, OrderStatus
from smartsales.models.products import Product
from smartsales.schemas.orders_schema import (
    OrderCreate,
    OrderItemCreate,
    OrderUpdate,
)


#
# 1. Criar pedido
#
def create_order_service(
    db: Session, data: OrderCreate, current_user
) -> Order:
    # 1. Verificar cliente
    cliente = db.get(Client, data.client_id)
    if not cliente:
        raise HTTPException(
            HTTPStatus.NOT_FOUND, detail='Cliente não encontrado.'
        )
    # Se for USER, só pode criar para clientes que sejam dele
    if (
        current_user.role == UserRole.USER
        and cliente.owner_id != current_user.id
    ):  # noqa: E501
        raise HTTPException(
            HTTPStatus.FORBIDDEN, detail='Não autorizado para este cliente.'
        )

    # 2. Verificar itens e calcular preços
    total_pedido = 0
    itens_detalhados: List[Tuple[OrderItemCreate, float, float]] = []
    for item_in in data.items:
        produto = db.get(Product, item_in.product_id)
        if not produto:
            raise HTTPException(
                HTTPStatus.NOT_FOUND,
                detail=f'Produto id={item_in.product_id} não encontrado.',
            )
        # Se USER, só pode usar produtos dele
        # if (
        #     current_user.role == UserRole.USER
        #     and produto.owner_id != current_user.id
        # ):  # noqa: E501
        #     raise HTTPException(
        #         HTTPStatus.FORBIDDEN,
        #         detail=f'Não autorizado para acessar o produto id={item_in.product_id}.',  # noqa: E501
        #     )
        if (produto.stock or 0) < item_in.quantity:
            raise HTTPException(
                HTTPStatus.BAD_REQUEST,
                detail=f'Estoque insuficiente para produto id={item_in.product_id}.',  # noqa: E501
            )
        unit_price = float(produto.sale_price)
        total_price = round(unit_price * item_in.quantity, 2)
        total_pedido += total_price
        itens_detalhados.append((item_in, unit_price, total_price))

    # 3. Criar Order
    novo_order = Order(
        client_id=data.client_id,
        status=data.status or OrderStatus.pending,
        total_value=total_pedido,
        owner_id=current_user.id,
    )
    db.add(novo_order)
    db.flush()  # para já obter novo_order.id

    # 4. Criar OrderItem e ajustar estoque
    for item_in, unit_price, total_price in itens_detalhados:
        oi = OrderItem(
            order_id=novo_order.id,
            product_id=item_in.product_id,
            quantity=item_in.quantity,
            unit_price=unit_price,
            total_price=total_price,
        )
        db.add(oi)
        # Ajustar estoque
        produto = db.get(Product, item_in.product_id)
        produto.stock = (produto.stock or 0) - item_in.quantity
        db.add(produto)

    db.commit()
    db.refresh(novo_order)
    return novo_order


#
# 2. Obter um pedido por ID
#
def get_order_service(db: Session, order_id: int, current_user) -> Order:
    stmt = (
        select(Order)
        .where(Order.id == order_id)
        .options(joinedload(Order.items))
    )
    result = db.execute(stmt)
    order_obj = result.unique().scalar_one_or_none()
    if not order_obj:
        raise HTTPException(
            HTTPStatus.NOT_FOUND, detail='Pedido não encontrado.'
        )

    if (
        current_user.role == UserRole.USER
        and order_obj.owner_id != current_user.id
    ):  # noqa: E501
        raise HTTPException(
            HTTPStatus.FORBIDDEN, detail='Não autorizado para este pedido.'
        )

    return order_obj


#
# 3. Listar pedidos com filtros e paginação
#
def list_orders_service(
    db: Session,
    current_user,
    skip: int = 0,
    limit: int = 10,
    client_id: Optional[int] = None,
    status: Optional[OrderStatus] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    section: Optional[str] = None,
    id_order: Optional[int] = None,
) -> Tuple[int, List[Order]]:
    """
    Retorna (total, lista de pedidos) com filtros:
      - client_id
      - status
      - período (date_from, date_to)
      - section de produto (join em OrderItem -> Product)
      - id_order
      - skip/limit para paginação

    Usa joinedload(Order.items),
    por isso precisa de `unique()` antes de `scalars()`.
    """

    stmt = select(Order)

    # 1) Filtrar por owner (quando for USER)
    if current_user.role == UserRole.USER:
        stmt = stmt.where(Order.owner_id == current_user.id)

    # 2) Aplicar filtros
    if id_order is not None:
        stmt = stmt.where(Order.id == id_order)

    if client_id is not None:
        stmt = stmt.where(Order.client_id == client_id)

    if status is not None:
        stmt = stmt.where(Order.status == status)

    if since is not None:
        stmt = stmt.where(Order.created_at >= since)

    if until is not None:
        stmt = stmt.where(Order.created_at <= until)

    if section:
        stmt = (
            stmt.join(OrderItem, Order.items)
            .join(Product, OrderItem.product)
            .where(Product.section.ilike(f'%{section}%'))
        )

    # 3) Contar total de registros (antes do offset/limit)
    total_q = stmt.with_only_columns(func.count()).order_by(None)
    total = db.execute(total_q).scalar() or 0

    # 4) Buscar objetos paginados, com joinedload e garantindo unicidade
    stmt = stmt.options(joinedload(Order.items)).order_by(
        Order.created_at.desc()
    )
    result = db.execute(stmt.offset(skip).limit(limit))
    pedidos = result.unique().scalars().all()

    return total, pedidos


#
# 4. Atualizar pedido
#
def update_order_service(
    db: Session, order_obj: Order, data: OrderUpdate, current_user
) -> Order:
    # 1. Reverter estoque dos itens antigos
    for item in order_obj.items:
        produto = db.get(Product, item.product_id)
        if produto:
            produto.stock = (produto.stock or 0) + item.quantity
            db.add(produto)

    # 2. Excluir itens antigos
    order_obj.items.clear()
    db.flush()

    # 3. Atualizar campos do pedido
    order_obj.client_id = data.client_id
    order_obj.status = data.status
    # vamos recalcular total_value a seguir
    total_novo = 0
    novos_detalhes: List[tuple[OrderItemCreate, float, float]] = []
    for item_in in data.items:
        produto = db.get(Product, item_in.product_id)
        if not produto:
            raise HTTPException(
                HTTPStatus.NOT_FOUND,
                detail=f'Produto id={item_in.product_id} não encontrado.',
            )
        if (produto.stock or 0) < item_in.quantity:
            raise HTTPException(
                HTTPStatus.BAD_REQUEST,
                detail=f'Estoque insuficiente para produto id={
                    item_in.product_id
                }.',
            )
        unit_price = float(produto.sale_price)
        total_price = round(unit_price * item_in.quantity, 2)
        total_novo += total_price
        novos_detalhes.append((item_in, unit_price, total_price))

    # 4. Criar novos OrderItem e ajustar estoque
    for item_in, unit_price, total_price in novos_detalhes:
        oi = OrderItem(
            order_id=order_obj.id,
            product_id=item_in.product_id,
            quantity=item_in.quantity,
            unit_price=unit_price,
            total_price=total_price,
        )
        db.add(oi)
        produto = db.get(Product, item_in.product_id)
        produto.stock = (produto.stock or 0) - item_in.quantity
        db.add(produto)

    # 5. Atualizar total_value e salvar
    order_obj.total_value = total_novo
    order_obj.updated_at = datetime.utcnow()
    db.add(order_obj)
    db.commit()
    db.refresh(order_obj)
    return order_obj


#
# 5. Excluir pedido (restitui estoque antes)
#
def delete_order_service(db: Session, order_obj: Order, current_user) -> None:
    """
    Devolve o estoque de cada OrderItem, depois exclui o pedido (cascade).
    """
    # 1. Verificar permissão (já garantida no controller antes de passar order_obj)  # noqa: E501
    # 2. Reverter estoque
    for item in order_obj.items:
        produto = db.get(Product, item.product_id)
        if produto:
            produto.stock = (produto.stock or 0) + item.quantity
            db.add(produto)

    # 3. Excluir pedido (itens são removidos em cascade)
    db.delete(order_obj)
    db.commit()
