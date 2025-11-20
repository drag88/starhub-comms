import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { utilityAPI } from '../services/api';
import type { Cohort, Product, Objective } from '../types/campaign';

interface ConfigContextType {
  cohorts: Cohort[];
  products: Product[];
  objectives: Objective[];
  isLoading: boolean;
  error: string | null;
  refreshConfig: () => Promise<void>;
}

const ConfigContext = createContext<ConfigContextType | undefined>(undefined);

export function ConfigProvider({ children }: { children: ReactNode }) {
  const [cohorts, setCohorts] = useState<Cohort[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [objectives, setObjectives] = useState<Objective[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadConfigurationData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [cohortsRes, productsRes, objectivesRes] = await Promise.all([
        utilityAPI.getCohorts(),
        utilityAPI.getProducts(),
        utilityAPI.getObjectives(),
      ]);

      setCohorts(cohortsRes.data.cohorts);
      setProducts(productsRes.data.products);
      setObjectives(objectivesRes.data.objectives);
    } catch (err: any) {
      console.error('Failed to load configuration:', err);
      setError('Failed to load application data. Please ensure the backend is running.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadConfigurationData();
  }, []);

  const value = {
    cohorts,
    products,
    objectives,
    isLoading,
    error,
    refreshConfig: loadConfigurationData,
  };

  return (
    <ConfigContext.Provider value={value}>
      {children}
    </ConfigContext.Provider>
  );
}

export function useConfig() {
  const context = useContext(ConfigContext);
  if (context === undefined) {
    throw new Error('useConfig must be used within a ConfigProvider');
  }
  return context;
}

