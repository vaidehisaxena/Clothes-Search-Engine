from pathlib import Path
root = Path('data')
root.mkdir(exist_ok=True)

categories = [
    'T-Shirt', 'Jeans', 'Dress', 'Jacket', 'Hoodie',
    'Skirt', 'Trouser', 'Sweater', 'Coat', 'Sneakers'
]

titles_by_category = {
    'T-Shirt': [
        "Men's Cotton Crew Neck T-Shirt - Black",
        "Women's V-Neck Cotton Tee - White",
        "Premium Graphic Tee - Navy",
        "Striped Cotton T-Shirt - Blue",
        "Oversized Heavy Cotton Tee - Grey",
        "Slim Fit Polo T-Shirt - Green",
        "Organic Cotton Crew Tee - Beige",
        "Cotton Blend T-Shirt - Red",
        "Performance Tee - Black",
        "Soft Jersey Tee - Pink",
    ],
    'Jeans': [
        'Classic Straight Leg Denim Jeans',
        'Skinny Stretch Denim Jeans',
        'Relaxed Fit Cotton Jeans',
        'Slim Dark Wash Denim',
        'High Rise Wide Leg Jeans',
        'Low Rise Denim Jeans',
        'Vintage Blue Denim Pants',
        'Comfort Stretch Denim Trousers',
        'Black Rigid Denim Jeans',
        'Cropped Denim Jeans',
    ],
    'Dress': [
        'Summer Floral Midi Dress',
        'Elegant Satin Evening Dress',
        'Casual Cotton Shirt Dress',
        'Maxi Wrap Dress - Navy',
        'Flowy Printed Sundress',
        'Knee Length Party Dress',
        'Off Shoulder Casual Dress',
        'A Line Cotton Dress',
        'Rib Knit Bodycon Dress',
        'Pleated Midi Dress',
    ],
    'Jacket': [
        'Lightweight Windproof Jacket',
        'Travel Utility Zip Jacket',
        'Classic Bomber Jacket',
        'Water Resistant Outdoor Jacket',
        'Tailored Wool Blend Jacket',
        'Softshell Hiking Jacket',
        'Casual Denim Jacket',
        'Puffer Insulated Jacket',
        'Leather Moto Jacket',
        'Packable Rain Jacket',
    ],
    'Hoodie': [
        'Cotton Fleece Hoodie',
        'Zip Through Hoodie',
        'Oversized Street Hoodie',
        'Heavyweight Basic Hoodie',
        'Cotton Blend Hoodie',
        'Pullover Hoodie - Grey',
        'Zipped Hoodie with Pockets',
        'Soft Knit Hoodie',
        'Athletic Performance Hoodie',
        'Warm Winter Hoodie',
    ],
    'Skirt': [
        'Pleated A-Line Skirt',
        'High Waist Denim Skirt',
        'Flowy Cotton Midi Skirt',
        'Wrap Satin Skirt',
        'Pleated Tennis Skirt',
        'Soft Stretch Pencil Skirt',
        'Flared Casual Skirt',
        'Layered Party Skirt',
        'Tailored Wool Skirt',
        'Printed Summer Skirt',
    ],
    'Trouser': [
        'Classic Chino Trouser',
        'Stretch Office Trousers',
        'Straight Fit Cotton Trouser',
        'Relaxed Cargo Trousers',
        'Slim Fit Wool Trouser',
        'Tailored Pleated Trouser',
        'Lightweight Travel Trouser',
        'Urban Utility Trouser',
        'Wide Leg Linen Trouser',
        'Formal Business Trouser',
    ],
    'Sweater': [
        'Chunky Knit Winter Sweater',
        'Soft Cotton Crew Sweater',
        'Cashmere Blend Sweater',
        'Oversized Hoodie Sweater',
        'Fine Gauge Knit Sweater',
        'Striped Wool Sweater',
        'Ribbed Henley Sweater',
        'Cropped Knit Sweater',
        'Warm Fleece Sweater',
        'Lightweight Merino Sweater',
    ],
    'Coat': [
        'Long Wool Blend Coat',
        'Classic Trench Coat',
        'Structured Formal Coat',
        'Puffer Winter Coat',
        'Double-Breasted Wool Coat',
        'Waterproof Parka Coat',
        'Cashmere Longline Coat',
        'Quilted Lined Coat',
        'Leather Trench Coat',
        'Tailored Peacoat',
    ],
    'Sneakers': [
        'Classic White Canvas Sneakers',
        'Running Air Cushion Sneakers',
        'Leather Casual Sneakers',
        'Street Style Low Top Sneakers',
        'Comfort Mesh Trainers',
        'Sport Flex Sneakers',
        'Retro Court Sneakers',
        'Lightweight Walking Sneakers',
        'Fashion Slip On Sneakers',
        'Premium Everyday Sneakers',
    ],
}

text_templates = [
    'Made from soft cotton and breathable fabric for everyday comfort and easy wear.',
    'Designed for a relaxed fit with durable stitching and smooth finish.',
    'Comfort stretch fabric keeps movement easy while retaining shape.',
    'Made with premium quality material for daily use and lasting durability.',
    'Lightweight and comfortable with a clean modern style and versatile finish.',
    'Soft-touch fabric offers all-day comfort with a flattering silhouette.',
    'Crafted for daily wear with breathable comfort and a refined look.',
    'Premium construction combines comfort, style, and easy maintenance.',
    'Built for movement with flexible material and a polished appearance.',
    'Easy-care fabric keeps this product comfortable, stylish, and practical.',
]

count = 1
records = []
for category in categories:
    for title in titles_by_category[category]:
        doc_id = f'D{count:03d}'
        text = f'{title}. {text_templates[(count - 1) % len(text_templates)]}'
        records.append((doc_id, category, title, text))
        count += 1

path = root / 'corpus_100.txt'
with path.open('w', encoding='utf-8') as f:
    for doc_id, category, title, text in records:
        f.write('<DOC>\n')
        f.write(f'<DOCID>{doc_id}</DOCID>\n')
        f.write(f'<CATEGORY>{category}</CATEGORY>\n')
        f.write(f'<TITLE>{title}</TITLE>\n')
        f.write(f'<TEXT>{text}</TEXT>\n')
        f.write('</DOC>\n\n')

print(f'Created {len(records)} documents in {path}')
