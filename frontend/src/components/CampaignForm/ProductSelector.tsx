import React from 'react';
import type { Product } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/campaign';

interface ProductSelectorProps {
  products: Product[];
  selectedProducts: string[];
  onChange: (value: string[]) => void;
  error?: string;
}

export const ProductSelector: React.FC<ProductSelectorProps> = ({
  products,
  selectedProducts,
  onChange,
  error,
}) => {
  // Get unique categories from products (normalize to lowercase for consistency)
  const uniqueCategories = React.useMemo(() => {
    const categorySet = new Set<string>();
    products.forEach(product => {
      const category = (product.category || product.product_line || '').toLowerCase();
      if (category) {
        categorySet.add(category);
      }
    });
    return Array.from(categorySet).sort();
  }, [products]);

  const toggleProduct = (category: string) => {
    if (selectedProducts.includes(category)) {
      onChange(selectedProducts.filter(p => p !== category));
    } else {
      onChange([...selectedProducts, category]);
    }
  };

  return (
    <div>
      <label className="form-label">Product Lines</label>
      <div className="grid grid-cols-2 gap-3">
        {uniqueCategories.map((category) => (
          <label
            key={category}
            className={`flex items-center p-3 border-2 rounded-lg cursor-pointer transition-all ${
              selectedProducts.includes(category)
                ? 'border-primary-600 bg-primary-50'
                : 'border-gray-300 bg-white hover:border-primary-300'
            }`}
          >
            <input
              type="checkbox"
              className="mr-3"
              checked={selectedProducts.includes(category)}
              onChange={() => toggleProduct(category)}
            />
            <div>
              <div className="font-medium capitalize">{category}</div>
            </div>
          </label>
        ))}
      </div>
      {error && <p className="form-error">{error}</p>}
    </div>
  );
};
