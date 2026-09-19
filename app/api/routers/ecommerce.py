"""E-Commerce Store and Knowledge Base API endpoints for Frontend UI."""
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.services.database import db_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Ecommerce"])


@router.get("/customers", summary="Get all registered demo customers")
def get_customers():
    """Returns all customers with profile info, address, loyalty tier, and total spent."""
    try:
        return {"customers": db_service.get_all_customers()}
    except Exception as e:
        logger.exception("Failed to get customers")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products", summary="Search and list products")
def get_products(
    query: str = Query("", description="Search term"),
    category: Optional[str] = Query(None, description="Product category filter"),
    limit: int = Query(50, ge=1, le=100)
):
    """Returns products matching search query and/or category."""
    try:
        products = db_service.search_products(query=query, category=category, limit=limit)
        return {"products": products, "total": len(products)}
    except Exception as e:
        logger.exception("Failed to search products")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders/{customer_id}", summary="Get orders for a customer")
def get_customer_orders(customer_id: str):
    """Returns order history for a specific customer."""
    try:
        orders = db_service.get_orders_by_customer(customer_id)
        # Enrich with shipping tracking status if available
        for order in orders:
            tracking_num = order.get("tracking_number")
            if tracking_num:
                shipping = db_service.get_shipping(tracking_num)
                order["shipping_info"] = shipping
        return {"orders": orders, "customer_id": customer_id}
    except Exception as e:
        logger.exception("Failed to get orders for customer %s", customer_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders/detail/{order_id}", summary="Get full details for an order")
def get_order_detail(order_id: str):
    """Returns full order information including items, shipping, and payment details."""
    try:
        order = db_service.get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        tracking_num = order.get("tracking_number")
        shipping = db_service.get_shipping(tracking_num) if tracking_num else None
        payment = db_service.get_payment_by_order(order_id)
        return {
            "order": order,
            "shipping": shipping,
            "payment": payment,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get order %s", order_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kb-articles", summary="List knowledge base articles (policies, guides, FAQs)")
def get_kb_articles(
    category: Optional[str] = Query(None, description="Category filter (policy, guide, faq)"),
    query: str = Query("", description="Search term")
):
    """Returns knowledge base articles from SQLite database."""
    try:
        if query:
            articles = db_service.search_kb_articles(query=query, category=category, limit=50)
        else:
            articles = db_service.get_all_kb_articles(category=category)
        return {"articles": articles, "total": len(articles)}
    except Exception as e:
        logger.exception("Failed to get KB articles")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/troubleshooting", summary="List troubleshooting guides")
def get_troubleshooting():
    """Returns troubleshooting guides for common products and symptoms."""
    try:
        guides = db_service.get_all_troubleshooting()
        return {"guides": guides, "total": len(guides)}
    except Exception as e:
        logger.exception("Failed to get troubleshooting guides")
        raise HTTPException(status_code=500, detail=str(e))
