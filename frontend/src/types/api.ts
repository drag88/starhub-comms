export interface APIError {
  detail: string;
}

export interface PaginationParams {
  skip?: number;
  limit?: number;
}

export interface ListResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}
