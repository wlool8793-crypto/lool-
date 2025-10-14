# UI Components

This directory contains reusable UI components for the Hostel Meal Management System.

## Directory Structure

```
components/
├── common/          # Common utility components
├── layout/          # Layout components (sidebar, header, etc.)
├── forms/           # Form input components
├── dashboard/       # Dashboard-specific components
└── index.ts         # Central export file
```

## Components Overview

### Common Components

#### LoadingSpinner
A versatile loading spinner component with multiple sizes and display modes.

```tsx
import { LoadingSpinner } from '@/components';

// Basic usage
<LoadingSpinner />

// With message and custom size
<LoadingSpinner size="lg" message="Loading data..." />

// Full screen overlay
<LoadingSpinner fullScreen />
```

**Props:**
- `size`: 'sm' | 'md' | 'lg' | 'xl' (default: 'md')
- `className`: Additional CSS classes
- `fullScreen`: Display as full-screen overlay (default: false)
- `message`: Optional loading message

---

#### EmptyState
Display empty states with icons and optional actions.

```tsx
import { EmptyState } from '@/components';
import { Inbox } from 'lucide-react';

<EmptyState
  icon={Inbox}
  title="No meals found"
  description="Start by adding your first meal to the menu"
  action={{
    label: "Add Meal",
    onClick: () => navigate('/meals/new')
  }}
/>
```

**Props:**
- `icon`: LucideIcon component (default: Inbox)
- `title`: Main heading text
- `description`: Optional description text
- `action`: Optional action button { label, onClick }
- `className`: Additional CSS classes

---

#### ErrorBoundary
React error boundary for graceful error handling.

```tsx
import { ErrorBoundary } from '@/components';

<ErrorBoundary onError={(error, errorInfo) => logError(error)}>
  <YourApp />
</ErrorBoundary>

// With custom fallback
<ErrorBoundary fallback={<CustomErrorPage />}>
  <YourApp />
</ErrorBoundary>
```

**Props:**
- `children`: React components to wrap
- `fallback`: Custom error UI (optional)
- `onError`: Error callback function (optional)

---

### Layout Components

#### AppLayout
Main application layout with sidebar and header.

```tsx
import { AppLayout } from '@/components';

<AppLayout
  userName="John Doe"
  userRole="student"
  userAvatar="/avatar.jpg"
  notifications={[...]}
  onLogout={handleLogout}
>
  {/* Your routes will render here via <Outlet /> */}
</AppLayout>
```

**Props:**
- `userName`: User's display name
- `userRole`: 'admin' | 'manager' | 'student'
- `userAvatar`: Avatar image URL (optional)
- `notifications`: Array of notification objects (optional)
- `onLogout`: Logout handler function

---

#### Sidebar
Collapsible sidebar navigation with role-based menu items.

```tsx
import { Sidebar } from '@/components';

<Sidebar
  isCollapsed={isCollapsed}
  onToggle={() => setIsCollapsed(!isCollapsed)}
  userRole="student"
/>
```

**Props:**
- `isCollapsed`: Sidebar collapsed state
- `onToggle`: Toggle callback function
- `userRole`: User role for filtering menu items

**Menu Items:** Automatically filters based on user role:
- Dashboard (all roles)
- Meals (all roles)
- Menu Planning (admin, manager)
- Orders (all roles)
- Students (admin, manager)
- Reports (admin, manager)
- Feedback (all roles)
- Settings (all roles)

---

#### Header
Application header with notifications and user menu.

```tsx
import { Header } from '@/components';

<Header
  userName="John Doe"
  userRole="student"
  notifications={notifications}
  onLogout={handleLogout}
/>
```

**Props:**
- `userName`: User's display name
- `userRole`: User's role (displayed in dropdown)
- `userAvatar`: Avatar image URL (optional)
- `notifications`: Array of notification objects
- `onLogout`: Logout handler

**Notification Object:**
```ts
{
  id: string;
  title: string;
  message: string;
  time: string;
  read: boolean;
}
```

---

### Form Components

#### Input
Enhanced input field with validation, icons, and error handling.

```tsx
import { Input } from '@/components';
import { Mail } from 'lucide-react';

<Input
  label="Email"
  type="email"
  placeholder="Enter your email"
  leftIcon={<Mail className="w-5 h-5" />}
  error={errors.email}
  hint="We'll never share your email"
  required
/>
```

**Props:**
- Extends all standard HTML input props
- `label`: Field label
- `error`: Error message string
- `hint`: Help text below input
- `leftIcon`: Icon on the left side
- `rightIcon`: Icon on the right side
- `fullWidth`: Take full container width (default: true)

---

#### Select
Styled select dropdown with validation.

```tsx
import { Select } from '@/components';

<Select
  label="Meal Type"
  options={[
    { value: 'breakfast', label: 'Breakfast' },
    { value: 'lunch', label: 'Lunch' },
    { value: 'dinner', label: 'Dinner' }
  ]}
  placeholder="Choose meal type"
  error={errors.mealType}
  required
/>
```

**Props:**
- Extends all standard HTML select props
- `label`: Field label
- `options`: Array of { value, label, disabled? }
- `error`: Error message string
- `hint`: Help text below select
- `placeholder`: Placeholder option text
- `fullWidth`: Take full container width (default: true)

---

#### Button
Versatile button component with loading states and variants.

```tsx
import { Button } from '@/components';
import { Save, Plus } from 'lucide-react';

// Primary button
<Button variant="primary" size="md">
  Submit
</Button>

// With icons
<Button
  leftIcon={<Plus className="w-4 h-4" />}
  onClick={handleAdd}
>
  Add Meal
</Button>

// Loading state
<Button loading={isSubmitting}>
  Save Changes
</Button>

// Danger variant
<Button variant="danger" onClick={handleDelete}>
  Delete
</Button>
```

**Props:**
- Extends all standard HTML button props
- `variant`: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
- `size`: 'sm' | 'md' | 'lg'
- `loading`: Show loading spinner (default: false)
- `leftIcon`: Icon on the left
- `rightIcon`: Icon on the right
- `fullWidth`: Take full container width (default: false)

---

### Dashboard Components

#### StatCard
Statistical card for displaying metrics and trends.

```tsx
import { StatCard } from '@/components';
import { Users } from 'lucide-react';

<StatCard
  title="Total Students"
  value={256}
  icon={Users}
  color="blue"
  trend={{
    value: 12,
    isPositive: true,
    label: "from last month"
  }}
  description="Active registered students"
  onClick={() => navigate('/students')}
/>
```

**Props:**
- `title`: Card title/label
- `value`: Main metric value (string or number)
- `icon`: Lucide icon component
- `color`: 'blue' | 'green' | 'yellow' | 'red' | 'purple' | 'indigo'
- `trend`: Optional trend indicator { value, isPositive, label? }
- `description`: Additional description text
- `onClick`: Optional click handler (makes card clickable)

---

## Import Patterns

### Named Imports
```tsx
import { Button, Input, LoadingSpinner } from '@/components';
```

### Direct Imports
```tsx
import { Button } from '@/components/forms/Button';
import { Header } from '@/components/layout/Header';
```

## Styling

All components use:
- **Tailwind CSS** for styling
- **lucide-react** for icons
- **Responsive design** principles
- **Consistent color palette** (blue primary, gray neutrals)
- **Focus states** for accessibility

## Accessibility Features

- ARIA labels and roles
- Keyboard navigation support
- Focus indicators
- Screen reader friendly
- Proper semantic HTML

## Customization

All components accept a `className` prop for additional styling:

```tsx
<Button className="mt-4 shadow-lg">
  Custom Styled Button
</Button>
```

## Best Practices

1. **Use TypeScript**: All components are fully typed
2. **Handle errors**: Wrap sensitive areas with ErrorBoundary
3. **Loading states**: Use LoadingSpinner during async operations
4. **Empty states**: Show EmptyState when no data available
5. **Validation**: Use error props on form components
6. **Icons**: Import from lucide-react for consistency
