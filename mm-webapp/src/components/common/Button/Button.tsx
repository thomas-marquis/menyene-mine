import { type ReactNode, type ButtonHTMLAttributes, forwardRef } from 'react';
import { Button as BootstrapButton, Spinner } from 'react-bootstrap';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'danger' | 'outline' | 'outline-primary' | 'outline-secondary' | 'outline-danger';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  loading?: boolean;
}

// Map custom variant names to Bootstrap variants
const variantMap: Record<string, string> = {
  primary: 'primary',
  secondary: 'secondary',
  danger: 'danger',
  outline: 'outline-primary',
  'outline-primary': 'outline-primary',
  'outline-secondary': 'outline-secondary',
  'outline-danger': 'outline-danger',
};

// Map custom size names to Bootstrap sizes
const sizeMap: Record<string, string> = {
  small: 'sm',
  medium: 'md',
  large: 'lg',
  sm: 'sm',
  md: 'md',
  lg: 'lg',
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      variant = 'primary',
      size = 'md',
      fullWidth = false,
      loading = false,
      className = '',
      disabled,
      ...props
    },
    ref
  ) => {
    // Map variant and size to Bootstrap equivalents
    const bootstrapVariant = variantMap[variant] || variant;
    const bootstrapSize = sizeMap[size] || size;

    return (
      <BootstrapButton
        ref={ref}
        variant={bootstrapVariant as any}
        size={bootstrapSize as any}
        className={`d-inline-flex align-items-center justify-content-center gap-2 ${fullWidth ? 'w-100' : ''} ${className}`}
        disabled={disabled || loading}
        {...props}
      >
        {loading ? (
          <>
            <Spinner
              animation="border"
              size="sm"
              className="me-2"
              role="status"
              aria-hidden="true"
            />
            Loading...
          </>
        ) : (
          children
        )}
      </BootstrapButton>
    );
  }
);

Button.displayName = 'Button';
