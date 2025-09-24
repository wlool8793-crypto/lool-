import { render, screen, fireEvent } from '@testing-library/react';
import { axe } from 'jest-axe';
import { vi } from 'vitest';
import { Input, inputVariants } from '@/components/common/Input';
import { testComponentPerformance } from '@/test/performance';

describe('Input Component', () => {
  const baseProps = {
    placeholder: 'Test placeholder',
    'data-testid': 'test-input',
  };

  it('renders input with default props', () => {
    render(<Input {...baseProps} />);
    const input = screen.getByTestId('test-input');

    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('type', 'text');
    expect(input).toHaveAttribute('placeholder', 'Test placeholder');
    expect(input).toHaveClass('border-gray-300', 'bg-white');
  });

  it('renders with different types', () => {
    const types = ['text', 'email', 'password', 'number', 'tel', 'url'] as const;

    types.forEach(type => {
      const { unmount } = render(<Input type={type} {...baseProps} />);
      const input = screen.getByTestId('test-input');

      expect(input).toHaveAttribute('type', type);
      unmount();
    });
  });

  it('renders with error variant', () => {
    render(<Input variant="error" {...baseProps} />);
    const input = screen.getByTestId('test-input');

    expect(input).toHaveClass('border-red-500', 'focus-visible:ring-red-500');
  });

  it('handles value changes correctly', () => {
    const handleChange = vi.fn();
    render(<Input onChange={handleChange} {...baseProps} />);

    const input = screen.getByTestId('test-input');
    fireEvent.change(input, { target: { value: 'test value' } });

    expect(handleChange).toHaveBeenCalledTimes(1);
    expect(input).toHaveValue('test value');
  });

  it('handles focus and blur events', () => {
    const handleFocus = vi.fn();
    const handleBlur = vi.fn();

    render(
      <Input onFocus={handleFocus} onBlur={handleBlur} {...baseProps} />
    );

    const input = screen.getByTestId('test-input');

    fireEvent.focus(input);
    expect(handleFocus).toHaveBeenCalledTimes(1);

    fireEvent.blur(input);
    expect(handleBlur).toHaveBeenCalledTimes(1);
  });

  it('supports disabled state', () => {
    render(<Input disabled {...baseProps} />);
    const input = screen.getByTestId('test-input');

    expect(input).toBeDisabled();
    expect(input).toHaveClass('disabled:cursor-not-allowed', 'disabled:opacity-50');
  });

  it('supports readOnly state', () => {
    render(<Input readOnly value="read-only value" {...baseProps} />);
    const input = screen.getByTestId('test-input');

    expect(input).toHaveAttribute('readonly');
    expect(input).toHaveValue('read-only value');
  });

  it('supports required attribute', () => {
    render(<Input required {...baseProps} />);
    const input = screen.getByTestId('test-input');

    expect(input).toHaveAttribute('required');
  });

  it('supports custom className', () => {
    render(<Input className="custom-class" {...baseProps} />);
    const input = screen.getByTestId('test-input');

    expect(input).toHaveClass('custom-class');
  });

  it('supports additional HTML attributes', () => {
    render(
      <Input
        aria-label="Custom aria label"
        data-custom="custom-value"
        maxLength={100}
        minLength={5}
        {...baseProps}
      />
    );

    const input = screen.getByTestId('test-input');
    expect(input).toHaveAttribute('aria-label', 'Custom aria label');
    expect(input).toHaveAttribute('data-custom', 'custom-value');
    expect(input).toHaveAttribute('maxlength', '100');
    expect(input).toHaveAttribute('minlength', '5');
  });

  it('forwards ref correctly', () => {
    const ref = vi.fn();
    render(<Input ref={ref} {...baseProps} />);

    expect(ref).toHaveBeenCalled();
    expect(ref.mock.calls[0][0]).toBeInstanceOf(HTMLInputElement);
  });

  it('has proper accessibility attributes', async () => {
    const { container } = render(<Input aria-label="Test input" {...baseProps} />);

    // Test with axe
    const results = await axe(container);
    expect(results).toHaveNoViolations();

    const input = screen.getByTestId('test-input');
    expect(input).toHaveAccessibleName('Test input');
  });

  it('has proper accessibility for required input', async () => {
    const { container } = render(<Input required aria-label="Required input" {...baseProps} />);

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    const input = screen.getByTestId('test-input');
    expect(input).toHaveAttribute('required');
    expect(input).toHaveAccessibleName('Required input');
  });

  it('has proper accessibility for disabled input', async () => {
    const { container } = render(<Input disabled aria-label="Disabled input" {...baseProps} />);

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    const input = screen.getByTestId('test-input');
    expect(input).toBeDisabled();
  });

  it('performs well under load', async () => {
    const stats = await testComponentPerformance('Input', 100, () => {
      const { unmount } = render(<Input {...baseProps} />);
      unmount();
    });

    // Performance assertions are handled by testComponentPerformance function
    expect(stats).toBeDefined();
  });

  it('handles rapid value changes without performance issues', () => {
    const handleChange = vi.fn();
    const { unmount } = render(<Input onChange={handleChange} {...baseProps} />);
    const input = screen.getByTestId('test-input');

    const start = performance.now();
    for (let i = 0; i < 1000; i++) {
      fireEvent.change(input, { target: { value: `test ${i}` } });
    }
    const end = performance.now();

    const avgTime = (end - start) / 1000;
    expect(avgTime).toBeLessThan(0.5); // Should be very fast

    unmount();
  });

  it('has correct displayName', () => {
    expect(Input.displayName).toBe('Input');
  });

  it('exports inputVariants correctly', () => {
    expect(typeof inputVariants).toBe('function');
  });

  it('supports file input type', () => {
    const handleChange = vi.fn();
    const { unmount } = render(<Input type="file" onChange={handleChange} {...baseProps} />);
    const input = screen.getByTestId('test-input');

    expect(input).toHaveAttribute('type', 'file');
    unmount();
  });

  it('supports file input with multiple selection', () => {
    render(<Input type="file" multiple {...baseProps} />);
    const input = screen.getByTestId('test-input');

    expect(input).toHaveAttribute('multiple');
  });

  it('supports checkbox input type', () => {
    render(<Input type="checkbox" {...baseProps} />);
    const input = screen.getByTestId('test-input');

    expect(input).toHaveAttribute('type', 'checkbox');
  });

  it('supports radio input type', () => {
    render(<Input type="radio" {...baseProps} />);
    const input = screen.getByTestId('test-input');

    expect(input).toHaveAttribute('type', 'radio');
  });

  it('handles file selection correctly', () => {
    const handleChange = vi.fn();
    const { unmount } = render(<Input type="file" onChange={handleChange} {...baseProps} />);
    const input = screen.getByTestId('test-input');

    const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
    const fileList = createDataTransfer([file]);

    fireEvent.change(input, { target: { files: fileList.files } });

    expect(handleChange).toHaveBeenCalledTimes(1);
    unmount();
  });

  it('supports step attribute for number inputs', () => {
    render(<Input type="number" step="0.1" {...baseProps} />);
    const input = screen.getByTestId('test-input');

    expect(input).toHaveAttribute('step', '0.1');
  });

  it('supports min and max attributes for number inputs', () => {
    render(<Input type="number" min="0" max="100" {...baseProps} />);
    const input = screen.getByTestId('test-input');

    expect(input).toHaveAttribute('min', '0');
    expect(input).toHaveAttribute('max', '100');
  });

  it('supports pattern attribute for text inputs', () => {
    render(<Input pattern="[A-Za-z]{3}" {...baseProps} />);
    const input = screen.getByTestId('test-input');

    expect(input).toHaveAttribute('pattern', '[A-Za-z]{3}');
  });
});

// Helper function to create DataTransfer for file uploads
function createDataTransfer(files: File[]): DataTransfer {
  const dataTransfer = {
    files,
    items: files.map(file => ({
      kind: 'file' as const,
      type: file.type,
      getAsFile: () => file,
    })),
    // Add required DataTransfer properties
    dropEffect: 'none',
    effectAllowed: 'none',
    setData: () => {},
    getData: () => '',
    clearData: () => {},
    types: [],
    setDragImage: () => {},
  };
  return dataTransfer as unknown as DataTransfer;
}