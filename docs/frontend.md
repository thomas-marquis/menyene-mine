# Frontend


## Folder structure

**Important** The file names provided bellow are examples and not actual names

```
src/
│   mm-webapp/src/
│   ├── assets/                  # Static assets
│   │   ├── images/
│   │   ├── fonts/
│   │   └── icons/
│   │
│   ├── components/               # Reusable, UI components
│   │   ├── common/               # Buttons, Inputs, Modals, etc.
│   │   │   ├── Button/
│   │   │   │   ├── Button.jsx
│   │   │   │   ├── Button.module.css
│   │   │   │   ├── Button.test.jsx
│   │   │   │   └── index.js
│   │   │   └── Modal/
│   │   └── layout/               # Header, Footer, Sidebar, Navbar
│   │       ├── Header/
│   │       └── Footer/
│   │
│   ├── features/                 # Feature-based modules (recommended for scale)
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── services/         # API calls specific to auth
│   │   │   ├── authSlice.js      # Redux slice / Zustand store
│   │   │   └── index.js
│   │   ├── dashboard/
│   │   └── profile/
│   │
│   ├── pages/                    # Route-level components / views
│   │   ├── Home/
│   │   │   ├── Home.jsx
│   │   │   └── Home.module.css
│   │   ├── About/
│   │   └── NotFound/
│   │
│   ├── routes/                   # Routing configuration
│   │   ├── AppRoutes.jsx
│   │   └── ProtectedRoute.jsx
│   ├── hooks/                    # Global/shared custom hooks
│   │   ├── useAuth.js
│   │   ├── useDebounce.js
│   │   └── useFetch.js
│   ├── store/                    # Global state management (Redux/Zustand/Recoil)
│   │   ├── index.js
│   │   └── slices/
│   │
│   ├── services/                 # API/axios instances, external service logic
│   │   ├── api.js                # Axios instance/config
│   │   ├── authService.js
│   │   └── userService.js
│   ├── utils/                    # Helper/utility functions
│   │   ├── formatDate.js
│   │   ├── validators.js
│   │   └── constants.js
│   │
│   ├── types/                    # TypeScript types/interfaces (if using TS)
│   │   ├── user.types.ts
│   │   └── api.types.ts
│   │
│   ├── styles/                   # Global styles
│   │   ├── globals.css
│   │   ├── variables.css
│   │   └── theme.js              # If using styled-components/MUI theme
│   │
│   ├── config/                   # App-level configuration
│   │   ├── env.js
│   │   └── appConfig.js

```


## State management

State managed with react-redux.

