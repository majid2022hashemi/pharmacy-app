from enum import Enum


class Permission(str, Enum):
    CREATE_PURCHASE = "create_purchase"
    CREATE_SALE = "create_sale"
    CHANGE_PRICE = "change_price"
    MANAGE_INVENTORY = "manage_inventory"
    MANAGE_USERS = "manage_users"
    VIEW_REPORTS = "view_reports"
    MANAGE_RETURNS = "manage_returns"
