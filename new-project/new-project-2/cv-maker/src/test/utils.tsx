import { render, RenderOptions } from '@testing-library/react';
import { ReactElement } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from '../i18n';

// Custom render function with providers
export function renderWithProviders(
  ui: ReactElement,
  { ...renderOptions }: RenderOptions = {}
) {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <BrowserRouter>
        <I18nextProvider i18n={i18n}>
          {children}
        </I18nextProvider>
      </BrowserRouter>
    );
  }
  return { ...render(ui, { wrapper: Wrapper, ...renderOptions }) };
}

// Mock file data for testing
export const createMockFile = (name: string, type: string, size: number = 1024): File => {
  const blob = new Blob(['mock file content'], { type });
  return new File([blob], name, { type });
};

// Mock image data for testing
export const createMockImage = (width: number = 100, height: number = 100): string => {
  return `data:image/svg+xml;base64,${btoa(
    `<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
      <rect width="${width}" height="${height}" fill="#ccc"/>
    </svg>`
  )}`;
};

// Wait for async operations
export const waitForAsync = () => new Promise(resolve => setTimeout(resolve, 0));

// Mock PDF generation
export const mockPDFGeneration = () => {
  const mockPDF = {
    save: vi.fn(),
    output: vi.fn(() => Promise.resolve(new Blob(['mock pdf content']))),
  };

  vi.mock('jspdf', () => ({
    default: vi.fn(() => mockPDF),
  }));

  return mockPDF;
};

// Mock file upload
export const mockFileUpload = (files: File[] = []) => {
  const dataTransfer = {
    files,
    items: files.map(file => ({
      kind: 'file' as const,
      type: file.type,
      getAsFile: () => file,
    })),
  };

  return dataTransfer;
};