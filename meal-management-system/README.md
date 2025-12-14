# Hostel Meal Management System

A comprehensive web application for managing hostel meal planning, expenses, deposits, and financial tracking. Built with React, TypeScript, and Supabase.

## Overview

The Hostel Meal Management System streamlines the process of managing meals in student hostels. It provides separate interfaces for students and managers, allowing students to plan their meals and track finances, while managers can oversee operations, manage expenses, and generate reports.

## Key Features

### For Students
- **Meal Planning**: Plan meals (breakfast, lunch, dinner) with deadline-based system
- **Financial Dashboard**: View deposits, meal costs, and remaining balance
- **Guest Meals**: Request meals for guests with pricing
- **Real-time Notifications**: Get alerts for deadlines and important updates
- **Profile Management**: Update personal information and profile picture
- **Menu Viewing**: Check daily meal menus
- **Transparent Expenses**: View all hostel expenses for full transparency

### For Managers
- **Student Management**: Add, edit, and manage student accounts
- **Expense Tracking**: Record and categorize all hostel expenses
- **Deposit Management**: Track student deposits and payments
- **Meal Reports**: View meal counts and statistics
- **Menu Management**: Create and update daily meal menus
- **Settings Configuration**: Set meal deadlines, pricing, and penalties
- **Announcements**: Send announcements to all students
- **Financial Reports**: Generate comprehensive financial reports

### System Features
- **Role-Based Access Control**: Separate permissions for students and managers
- **Real-time Updates**: Live data synchronization using Supabase Realtime
- **Deadline Management**: Automatic meal locking based on configurable deadlines
- **Cost Calculation**: Automatic calculation of meal costs and balances
- **Storage Integration**: Upload receipts and profile pictures
- **Row Level Security**: Database-level security policies
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Tech Stack

### Frontend
- **React 18.2** - UI library
- **TypeScript 5.2** - Type safety
- **Vite 5.0** - Build tool and dev server
- **React Router 6** - Client-side routing
- **Tailwind CSS 3.4** - Utility-first CSS framework
- **Lucide React** - Icon library
- **date-fns** - Date manipulation
- **Recharts** - Data visualization
- **React Hot Toast** - Toast notifications
- **Axios** - HTTP client

### Backend
- **Supabase** - Backend as a Service
  - PostgreSQL database
  - Authentication
  - Real-time subscriptions
  - Storage (file uploads)
  - Row Level Security (RLS)

### Development Tools
- **ESLint** - Code linting
- **TypeScript ESLint** - TypeScript-specific linting
- **PostCSS** - CSS processing
- **Autoprefixer** - CSS vendor prefixing

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (version 16.x or higher)
- **npm** (version 8.x or higher) or **yarn**
- **Git**
- A **Supabase** account (free tier available)
- A code editor (VS Code recommended)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd meal-management-system
```

### 2. Install Dependencies

```bash
npm install
```

Or using yarn:

```bash
yarn install
```

### 3. Environment Configuration

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Update the `.env` file with your Supabase credentials:

```env
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

You'll get these values from your Supabase project dashboard (see Supabase Setup section).

## Supabase Setup

For detailed Supabase setup instructions, see [SUPABASE_SETUP.md](./SUPABASE_SETUP.md).

### Quick Setup

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to SQL Editor and run the migrations:
   - First: `supabase/migrations/001_initial_schema.sql`
   - Second: `supabase/migrations/002_rls_policies.sql`
3. Create storage buckets:
   - `profile-pictures` (public)
   - `expense-receipts` (private)
4. Copy your project URL and anon key to `.env`

## Running Locally

### Development Server

Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Build for Production

Create a production build:

```bash
npm run build
```

The build output will be in the `dist` directory.

### Preview Production Build

Preview the production build locally:

```bash
npm run preview
```

## Deployment

For detailed deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md).

### Quick Deploy to Vercel

1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com) and import your repository
3. Add environment variables:
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`
4. Deploy!

## Project Structure

```
meal-management-system/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── common/         # Common components (Button, Input, etc.)
│   │   ├── dashboard/      # Dashboard-specific components
│   │   ├── forms/          # Form components
│   │   └── layout/         # Layout components (Header, Sidebar)
│   ├── contexts/           # React contexts (AuthContext)
│   ├── hooks/              # Custom React hooks
│   │   ├── useAuth.ts      # Authentication hook
│   │   ├── useMeals.ts     # Meals management hook
│   │   └── useRealtime.ts  # Realtime subscriptions hook
│   ├── pages/              # Page components
│   │   ├── auth/           # Authentication pages (Login, Register)
│   │   ├── student/        # Student pages
│   │   └── manager/        # Manager pages
│   ├── services/           # API services
│   │   ├── auth.service.ts        # Authentication
│   │   ├── meals.service.ts       # Meals management
│   │   ├── deposits.service.ts    # Deposits management
│   │   ├── expenses.service.ts    # Expenses management
│   │   ├── users.service.ts       # User management
│   │   ├── menu.service.ts        # Menu management
│   │   ├── settings.service.ts    # Settings management
│   │   ├── notifications.service.ts # Notifications
│   │   ├── announcements.service.ts # Announcements
│   │   └── supabase.ts            # Supabase client
│   ├── types/              # TypeScript type definitions
│   ├── App.tsx             # Main App component with routing
│   ├── main.tsx            # Entry point
│   └── index.css           # Global styles
├── supabase/
│   └── migrations/         # Database migrations
│       ├── 001_initial_schema.sql
│       └── 002_rls_policies.sql
├── public/                 # Static assets
├── .env.example           # Environment variables template
├── package.json           # Dependencies and scripts
├── tsconfig.json          # TypeScript configuration
├── vite.config.ts         # Vite configuration
└── tailwind.config.js     # Tailwind CSS configuration
```

## Database Schema

### Main Tables

- **users** - Student and manager profiles
- **meals** - Daily meal planning records
- **deposits** - Student deposit records
- **expenses** - Hostel expense records
- **meal_settings** - Deadline and pricing configuration
- **menu** - Daily meal menus
- **announcements** - System announcements
- **notifications** - User notifications

### Key Views

- **meal_counts_by_date** - Aggregated meal statistics
- **student_financial_summary** - Student financial overview

## User Guide

For detailed user instructions, see [USER_GUIDE.md](./USER_GUIDE.md).

### Quick Start for Students

1. **Register/Login**: Create an account or log in
2. **Plan Meals**: Go to Meal Planner and select your meals for upcoming days
3. **Add Guests**: If expecting guests, add guest meals
4. **View Finances**: Check your deposits and meal costs in Financial Summary
5. **Check Menu**: View daily meal menus
6. **Update Profile**: Keep your profile information current

### Quick Start for Managers

1. **Login**: Use your manager credentials
2. **Add Students**: Manage student accounts
3. **Record Deposits**: Track student payments
4. **Add Expenses**: Record daily expenses with receipts
5. **View Reports**: Monitor meal counts and financial reports
6. **Set Menu**: Update daily meal menus
7. **Configure Settings**: Set deadlines and pricing

## Configuration

### Meal Deadlines

Deadlines prevent late meal cancellations:

- **Breakfast**: Default 8:00 AM (same day)
- **Lunch**: Default 1:00 PM (same day)
- **Dinner**: Default 8:00 PM (previous day)

Managers can configure these in Settings.

### Pricing Structure

- **Fixed Meal Cost**: Optional fixed price per meal
- **Variable Cost**: Calculated based on monthly expenses / total meals
- **Guest Meal Price**: Fixed price for guest meals
- **Late Cancellation Penalty**: Optional penalty for missed deadlines

## Troubleshooting

### Common Issues

#### 1. Supabase Connection Error

**Problem**: "Failed to connect to Supabase"

**Solution**:
- Check your `.env` file has correct credentials
- Verify your Supabase project is active
- Check network connectivity
- Ensure environment variables start with `VITE_`

#### 2. Authentication Not Working

**Problem**: Cannot log in or register

**Solution**:
- Run both migration files in order
- Check RLS policies are enabled
- Verify email confirmation settings in Supabase
- Check browser console for errors

#### 3. Meal Updates Not Saving

**Problem**: Meal changes don't persist

**Solution**:
- Check if deadline has passed (meals are locked)
- Verify RLS policies allow updates
- Check network connectivity
- Clear browser cache

#### 4. File Upload Failing

**Problem**: Cannot upload profile pictures or receipts

**Solution**:
- Verify storage buckets exist in Supabase
- Check bucket permissions
- Ensure file size is under limit (2MB recommended)
- Check file format (jpg, png, pdf)

#### 5. Build Errors

**Problem**: `npm run build` fails

**Solution**:
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
npm run build
```

#### 6. Environment Variables Not Loading

**Problem**: Configuration not being read

**Solution**:
- Ensure `.env` file is in root directory
- Restart dev server after changing `.env`
- Variables must start with `VITE_`
- Don't commit `.env` to git

#### 7. Port Already in Use

**Problem**: "Port 3000 is already in use"

**Solution**:
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or change port in vite.config.ts
```

## Performance Optimization

### Best Practices

1. **Image Optimization**
   - Compress images before upload
   - Use appropriate file formats
   - Implement lazy loading

2. **Data Fetching**
   - Use pagination for large lists
   - Implement data caching
   - Use Supabase real-time selectively

3. **Code Splitting**
   - Lazy load routes
   - Dynamic imports for heavy components

4. **Database Optimization**
   - Use indexes (already configured)
   - Optimize queries
   - Use views for complex aggregations

## Security Considerations

### Implemented Security Features

- **Row Level Security (RLS)**: Database-level access control
- **Authentication**: Supabase Auth with JWT tokens
- **Role-Based Access**: Separate permissions for students/managers
- **Secure Storage**: Private buckets for sensitive documents
- **Input Validation**: Both client and server-side
- **SQL Injection Prevention**: Parameterized queries via Supabase

### Security Best Practices

1. Never commit `.env` file to version control
2. Use strong passwords for manager accounts
3. Regularly update dependencies
4. Monitor Supabase audit logs
5. Enable two-factor authentication for Supabase account
6. Regularly backup database
7. Review and update RLS policies as needed

## Future Enhancements

### Planned Features

- [ ] **Mobile App**: React Native mobile application
- [ ] **Email Notifications**: Automated email reminders
- [ ] **SMS Notifications**: SMS alerts for deadlines
- [ ] **Advanced Reporting**: Export reports to PDF/Excel
- [ ] **Attendance Tracking**: Track actual meal consumption
- [ ] **Inventory Management**: Track grocery and supplies
- [ ] **Automated Billing**: Monthly bill generation
- [ ] **Payment Gateway**: Online payment integration
- [ ] **Multi-Hostel Support**: Manage multiple hostels
- [ ] **Analytics Dashboard**: Advanced analytics and insights
- [ ] **Recipe Management**: Store and share recipes
- [ ] **Dietary Preferences**: Track allergies and preferences
- [ ] **Feedback System**: Collect student feedback on meals
- [ ] **Calendar Integration**: Sync with Google/Outlook calendars
- [ ] **Dark Mode**: Theme customization

### Nice to Have

- Push notifications
- Multi-language support
- Progressive Web App (PWA)
- Offline mode
- Chat/messaging between students and managers
- QR code-based check-in
- Integration with accounting software
- Meal rating system

## Contributing

We welcome contributions! Here's how you can help:

### Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contribution Guidelines

- Follow the existing code style
- Write meaningful commit messages
- Add comments for complex logic
- Update documentation for new features
- Test your changes thoroughly
- Ensure all builds pass
- Keep PRs focused on a single feature/fix

### Code Style

- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks
- Implement proper error handling
- Write reusable components
- Keep components small and focused
- Use meaningful variable names

### Reporting Bugs

When reporting bugs, include:
- Description of the issue
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots if applicable
- Environment details (OS, browser, Node version)

## Testing

### Running Tests

```bash
npm run test
```

### Test Coverage

```bash
npm run test:coverage
```

### Manual Testing Checklist

- [ ] User registration and login
- [ ] Meal planning and updates
- [ ] Deposit recording
- [ ] Expense tracking
- [ ] Report generation
- [ ] File uploads
- [ ] Real-time updates
- [ ] Mobile responsiveness

## Support

For support and questions:

- Create an issue on GitHub
- Check existing documentation
- Review troubleshooting section
- Contact system administrator

## License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2024 Hostel Meal Management System

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Acknowledgments

- Built with [React](https://react.dev/)
- Powered by [Supabase](https://supabase.com)
- Styled with [Tailwind CSS](https://tailwindcss.com)
- Icons by [Lucide](https://lucide.dev)

## Changelog

### Version 1.0.0 (Current)

- Initial release
- Student meal planning
- Manager dashboard
- Expense tracking
- Deposit management
- Real-time notifications
- File uploads
- Financial reporting

---

Made with care for hostel communities worldwide.
