export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: string;
  updatedAt: string;
}

export interface UserProfile extends User {
  phone?: string;
  avatar?: string;
  bio?: string;
  location?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials extends LoginCredentials {
  name: string;
  phone?: string;
}

export interface UpdateProfileCredentials {
  name?: string;
  phone?: string;
  bio?: string;
  location?: string;
  avatar?: File;
}

export interface ChangePasswordCredentials {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}
