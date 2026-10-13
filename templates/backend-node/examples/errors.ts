// Worked example: typed errors mapped to RFC 9457 problem+json (BE-4).
export abstract class AppError extends Error {
  abstract readonly status: number;
  abstract readonly type: string;          // stable URI, documented in openapi.yaml
  constructor(message: string, readonly detail?: Record<string, unknown>, options?: ErrorOptions) {
    super(message, options);
    this.name = new.target.name;
  }
}
export class NotFoundError extends AppError { readonly status = 404; readonly type = "https://errors.example.com/not-found"; }
export class ValidationError extends AppError { readonly status = 400; readonly type = "https://errors.example.com/validation"; }
export class ForbiddenError extends AppError { readonly status = 403; readonly type = "https://errors.example.com/forbidden"; }
export class ConflictError extends AppError { readonly status = 409; readonly type = "https://errors.example.com/conflict"; }

export interface Problem { type: string; title: string; status: number; detail?: string; instance?: string; requestId: string; errors?: unknown }

export function toProblem(err: unknown, requestId: string, instance: string): Problem {
  if (err instanceof AppError) {
    return { type: err.type, title: err.message, status: err.status, instance, requestId, errors: err.detail };
  }
  // Unknown errors: never leak internals (A10:2025). The logger records the cause with requestId.
  return { type: "about:blank", title: "Internal Server Error", status: 500, instance, requestId };
}
