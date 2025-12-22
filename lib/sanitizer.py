def sanitizeYear(date):
    # Date format is 'DD MMM YYYY' 
    parts = date.split()
    if len(parts) == 3:
        return parts[2]  # Return the year part
    else:
        raise ValueError("Date format is incorrect")
    
def sanitizeSKU(skuLink):
    # SKU link format is '/sets/{sku}'
    parts = skuLink.split('/')
    if len(parts) >= 3:
        sku = parts[2]  # Return the SKU part
        if sku.startswith('gw-'):
            return sku[3:]  # Remove 'gw-' prefix
        return sku
    else:
        raise ValueError("SKU link format is incorrect")