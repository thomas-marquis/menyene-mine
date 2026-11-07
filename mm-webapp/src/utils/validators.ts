export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const isValidPassword = (
  password: string,
  minLength: number = 8
): boolean => {
  return password.length >= minLength;
};

export const isValidUsername = (
  username: string,
  minLength: number = 3,
  maxLength: number = 20
): boolean => {
  return (
    username.length >= minLength &&
    username.length <= maxLength &&
    /^[a-zA-Z0-9_]+$/.test(username)
  );
};

export const isValidPhone = (phone: string): boolean => {
  const phoneRegex = /^\+?[\d\s-()]{10,}$/;
  return phoneRegex.test(phone);
};

export const isRequired = (value: any): boolean => {
  return value !== undefined && value !== null && value !== '';
};

export const isValidURL = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

export const validateForm = (
  values: Record<string, any>,
  validators: Record<string, (value: any) => boolean>
): { isValid: boolean; errors: Record<string, string> } => {
  const errors: Record<string, string> = {};
  let isValid = true;

  for (const [field, validator] of Object.entries(validators)) {
    if (values[field] !== undefined && !validator(values[field])) {
      errors[field] = `${field} is invalid`;
      isValid = false;
    }
  }

  return { isValid, errors };
};
