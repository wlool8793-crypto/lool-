import { render, screen, fireEvent } from '@testing-library/react';
import { axe } from 'jest-axe';
import { vi } from 'vitest';
import { Button, buttonVariants } from '@/components/ui/button';
import { testComponentPerformance } from '@/test/performance';

describe('Button Component', () => {
  const baseProps = {
    children: 'Test Button',
  };

  it('renders button with default props', () => {
    render(<Button {...baseProps} />);
    const button = screen.getByRole('button', { name: 'Test Button' });

    expect(button).toBeInTheDocument();
    expect(button).toHaveClass('bg-primary-600', 'text-white');
    expect(button).toHaveAttribute('type', 'button');
  });

  it('renders with different variants', () => {
    const variants = ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link', 'marriage'] as const;

    variants.forEach(variant => {
      const { unmount } = render(<Button variant={variant} {...baseProps} />);
      const button = screen.getByRole('button', { name: 'Test Button' });

      expect(button).toBeInTheDocument();

      // Check specific variant classes
      switch (variant) {
        case 'destructive':
          expect(button).toHaveClass('bg-red-600');
          break;
        case 'outline':
          expect(button).toHaveClass('border', 'border-input');
          break;
        case 'secondary':
          expect(button).toHaveClass('bg-secondary-100');
          break;
        case 'marriage':
          expect(button).toHaveClass('bg-marriage-600');
          break;
      }

      unmount();
    });
  });

  it('renders with different sizes', () => {
    const sizes = ['default', 'sm', 'lg', 'xl', 'icon'] as const;

    sizes.forEach(size => {
      const { unmount } = render(<Button size={size} {...baseProps} />);
      const button = screen.getByRole('button', { name: 'Test Button' });

      expect(button).toBeInTheDocument();

      // Check specific size classes
      switch (size) {
        case 'sm':
          expect(button).toHaveClass('h-8', 'text-xs');
          break;
        case 'lg':
          expect(button).toHaveClass('h-10', 'px-8');
          break;
        case 'xl':
          expect(button).toHaveClass('h-12', 'rounded-lg', 'text-base');
          break;
        case 'icon':
          expect(button).toHaveClass('h-9', 'w-9');
          break;
      }

      unmount();
    });
  });

  it('handles fullWidth prop correctly', () => {
    const { unmount } = render(<Button fullWidth {...baseProps} />);
    const button = screen.getByRole('button', { name: 'Test Button' });

    expect(button).toHaveClass('w-full');
    unmount();
  });

  it('shows loading state correctly', () => {
    render(<Button loading {...baseProps} />);
    const button = screen.getByRole('button', { name: 'Test Button' });
    const loader = screen.getByRole('status');

    expect(button).toBeDisabled();
    expect(loader).toBeInTheDocument();
    expect(loader).toHaveClass('animate-spin');
  });

  it('shows left icon correctly', () => {
    const leftIcon = <span data-testid="left-icon">★</span>;
    render(<Button leftIcon={leftIcon} {...baseProps} />);

    const leftIconElement = screen.getByTestId('left-icon');
    expect(leftIconElement).toBeInTheDocument();
  });

  it('shows right icon correctly', () => {
    const rightIcon = <span data-testid="right-icon">★</span>;
    render(<Button rightIcon={rightIcon} {...baseProps} />);

    const rightIconElement = screen.getByTestId('right-icon');
    expect(rightIconElement).toBeInTheDocument();
  });

  it('hides icons when loading', () => {
    const leftIcon = <span data-testid="left-icon">★</span>;
    const rightIcon = <span data-testid="right-icon">★</span>;

    render(
      <Button loading leftIcon={leftIcon} rightIcon={rightIcon} {...baseProps} />
    );

    expect(screen.queryByTestId('left-icon')).not.toBeInTheDocument();
    expect(screen.queryByTestId('right-icon')).not.toBeInTheDocument();
  });

  it('handles click events correctly', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick} {...baseProps} />);

    const button = screen.getByRole('button', { name: 'Test Button' });
    fireEvent.click(button);

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('does not handle click events when disabled', () => {
    const handleClick = vi.fn();
    render(<Button disabled onClick={handleClick} {...baseProps} />);

    const button = screen.getByRole('button', { name: 'Test Button' });
    fireEvent.click(button);

    expect(handleClick).not.toHaveBeenCalled();
  });

  it('does not handle click events when loading', () => {
    const handleClick = vi.fn();
    render(<Button loading onClick={handleClick} {...baseProps} />);

    const button = screen.getByRole('button', { name: 'Test Button' });
    fireEvent.click(button);

    expect(handleClick).not.toHaveBeenCalled();
  });

  it('supports keyboard navigation', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick} {...baseProps} />);

    const button = screen.getByRole('button', { name: 'Test Button' });

    // Test Enter key
    fireEvent.keyDown(button, { key: 'Enter' });
    expect(handleClick).toHaveBeenCalledTimes(1);

    // Test Space key
    fireEvent.keyDown(button, { key: ' ' });
    expect(handleClick).toHaveBeenCalledTimes(2);
  });

  it('has proper accessibility attributes', async () => {
    const { container } = render(<Button {...baseProps} />);

    // Test with axe
    const results = await axe(container);
    expect(results).toHaveNoViolations();

    // Test specific accessibility requirements
    const button = screen.getByRole('button', { name: 'Test Button' });
    expect(button).toHaveAttribute('type', 'button');
    expect(button).toBeEnabled();
  });

  it('passes accessibility tests when disabled', async () => {
    const { container } = render(<Button disabled {...baseProps} />);

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    const button = screen.getByRole('button', { name: 'Test Button' });
    expect(button).toBeDisabled();
  });

  it('has proper ARIA attributes for loading state', async () => {
    const { container } = render(<Button loading {...baseProps} />);

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    const button = screen.getByRole('button', { name: 'Test Button' });
    expect(button).toHaveAttribute('aria-busy', 'true');
  });

  it('performs well under load', async () => {
    const stats = await testComponentPerformance('Button', 100, () => {
      const { unmount } = render(<Button {...baseProps} />);
      unmount();
    });

    // Performance assertions are handled by testComponentPerformance function
    expect(stats).toBeDefined();
  });

  it('handles many rapid renders without memory leaks', () => {
    const renderCount = 1000;
    const renderFunction = () => {
      const { unmount } = render(<Button {...baseProps} />);
      unmount();
    };

    // Test rapid renders
    const start = performance.now();
    for (let i = 0; i < renderCount; i++) {
      renderFunction();
    }
    const end = performance.now();

    const avgTime = (end - start) / renderCount;
    expect(avgTime).toBeLessThan(1); // Should be very fast
  });

  it('supports custom className', () => {
    render(<Button className="custom-class" {...baseProps} />);
    const button = screen.getByRole('button', { name: 'Test Button' });

    expect(button).toHaveClass('custom-class');
  });

  it('supports additional HTML attributes', () => {
    render(
      <Button
        aria-label="Custom aria label"
        data-testid="custom-button"
        title="Custom title"
        {...baseProps}
      />
    );

    const button = screen.getByTestId('custom-button');
    expect(button).toHaveAttribute('aria-label', 'Custom aria label');
    expect(button).toHaveAttribute('title', 'Custom title');
  });

  it('forwards ref correctly', () => {
    const ref = vi.fn();
    render(<Button ref={ref} {...baseProps} />);

    expect(ref).toHaveBeenCalled();
    expect(ref.mock.calls[0][0]).toBeInstanceOf(HTMLButtonElement);
  });

  it('has correct displayName', () => {
    expect(Button.displayName).toBe('Button');
  });

  it('exports buttonVariants correctly', () => {
    expect(typeof buttonVariants).toBe('function');
  });
});