def generate_po(product_name: str, product_id: str, quantity: int, date_str: str) -> str:
    po_text = f"""PURCHASE ORDER

Product: {product_id}
Name: {product_name}
Quantity: {quantity}
Date: {date_str}

Please supply the above items at the earliest. We expect standard quality constraints applied as per previous agreements. 

Authorized by: Automated AI Agent Workflow"""

    return po_text

def generate_discount_letter(product_name: str, product_id: str) -> str:
    letter = f"""SUBJECT: Request for Discount

We request a discount for bulk purchase / surplus marketing assistance of Product: {product_name} ({product_id}).

Due to recent demand forecast shifts, our current inventory levels reflect a surplus footprint for this category segment. 

Looking forward to your response.

Authorized by: Automated AI Agent Workflow"""

    return letter
