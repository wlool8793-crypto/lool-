# CLAUDE.md


This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Essential Commands
- `npm run dev` - Start development server (automatically finds available port, typically 3000+)
- `npm run build` - Build for production (includes TypeScript compilation)
- `npm run lint` - Run ESLint
- `npm run preview` - Preview production build

### Testing Commands
- `npm test` - Run unit tests with Vitest
- `npm run test:ui` - Run tests with Vitest UI
- `npm run test:coverage` - Run tests with coverage report
- `npm run test:watch` - Run tests in watch mode
- `npm run test:e2e` - Run end-to-end tests with Playwright
- `npm run test:e2e:ui` - Run E2E tests with UI
- `npm run test:all` - Run both unit and E2E tests

### Specialized Testing
- `npm run test:perf` - Run performance-focused tests
- `npm run test:a11y` - Run accessibility tests

### Build Analysis
- `npm run build:analyze` - Build with bundle analysis

## Architecture Overview

### Dual-Document System
The application supports two distinct document types:
- **CV Maker**: Professional resume creation with 9-step process
- **Marriage Biodata**: Cultural marriage biodata with 11-step process

### State Management
- **CVContext**: Central state management using useReducer pattern
- **Document Switching**: Users can switch between CV and Marriage modes via navigation
- **Form Progress**: Separate progress tracking for each document type
- **Auto-save**: Automatic localStorage persistence

### Form Step Architecture
**CV Steps**: `['personal', 'summary', 'experience', 'education', 'skills', 'projects', 'certifications', 'languages', 'preview']`

**Marriage Steps**: `['personal', 'contact', 'family', 'education', 'occupation', 'lifestyle', 'partner-preference', 'horoscope', 'photos', 'about', 'preview']`

### Key Technical Patterns

#### Component Structure
- **FormSteps**: Individual step components for each form section
- **CVTemplates**: Template components for different document styles
- **Common**: Reusable UI components (Input, Select, Button, etc.)
- **DocumentRoutes**: Handles routing between document types and steps

#### Validation System
- **Zod Schemas**: Comprehensive validation in `src/validations/`
- **Separate Schema Files**: `cvSchemas.ts` and `marriageSchemas.ts`
- **Enum Configuration**: Updated to use `message` instead of deprecated `errorMap`

#### Type Safety
- **Strict TypeScript**: Full type definitions in `src/types/`
- **Separate Type Files**: `cv.ts`, `marriage.ts`, `common.ts`
- **Generic Components**: Type-safe reusable UI components

### Template System
- **CV Templates**: Modern, Traditional, Minimal designs
- **Marriage Templates**: Cultural and regional variations
- **PDF Export**: jsPDF + html2canvas integration
- **Real-time Preview**: Live preview updates as users type

### Internationalization
- **i18next**: Multi-language support
- **Language Context**: Language switching functionality
- **Locale Files**: Translation files in `src/assets/locales/`

### Testing Strategy
- **Unit Tests**: Component and utility testing with Vitest
- **E2E Tests**: Full user flow testing with Playwright
- **Accessibility**: Automated accessibility testing
- **Performance**: Performance benchmarking tests

### Development Server Notes
- **Port Detection**: Automatically finds available port (3000, 3001, etc.)
- **HMR**: Hot module replacement enabled
- **Live Links**: Check `access.html` for current working URLs

## Critical Implementation Details

### Marriage Biodata Steps Mapping
When working with marriage biodata, ensure all 11 steps are properly mapped in `DocumentRoutes.tsx`. Missing steps will cause the application to fail when navigating through the form.

### Zod Schema Validation
All enum configurations must use the updated syntax:
```typescript
// Correct
z.enum(['option1', 'option2'], { message: 'Error message' })

// Incorrect (deprecated)
z.enum(['option1', 'option2'], { errorMap: () => ({ message: 'Error message' }) })
```

### Context Actions
The CVContext supports both CV and Marriage biodata actions. Key action types:
- `UPDATE_MARRIAGE_DATA` for marriage biodata updates
- `NEXT_STEP` and `PREVIOUS_STEP` for navigation
- Document-specific update actions for each form section

### File Upload Configuration
Image uploads use react-dropzone with specific configurations for:
- Profile photos
- Document attachments
- Portfolio images
- Marriage biodata photos

### PDF Generation
PDF export uses:
- jsPDF for document generation
- html2canvas for HTML-to-image conversion
- Template-specific styling and layouts
- Quality and format configurations