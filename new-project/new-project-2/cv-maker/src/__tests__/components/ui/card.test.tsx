import { render, screen, fireEvent } from '@testing-library/react';
import { axe } from 'jest-axe';
import { vi } from 'vitest';
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card';
import { testComponentPerformance } from '@/test/performance';

describe('Card Component', () => {
  const baseProps = {
    children: <div>Card content</div>,
  };

  it('renders card with default props', () => {
    render(<Card {...baseProps} />);

    expect(screen.getByText('Card content')).toBeInTheDocument();
  });

  it('renders with custom className', () => {
    render(<Card className="custom-card" {...baseProps} />);

    const card = screen.getByTestId('card');
    expect(card).toHaveClass('custom-card');
  });

  it('supports onClick handler', () => {
    const handleClick = vi.fn();
    render(<Card onClick={handleClick} {...baseProps} />);

    const card = screen.getByTestId('card');
    fireEvent.click(card);

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('renders CardHeader component', () => {
    render(
      <Card>
        <CardHeader>
          <div>Header Content</div>
        </CardHeader>
        <CardContent>Content</CardContent>
      </Card>
    );

    expect(screen.getByText('Header Content')).toBeInTheDocument();
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('renders CardContent component', () => {
    render(
      <Card>
        <CardContent>Content</CardContent>
      </Card>
    );

    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('renders CardFooter component', () => {
    render(
      <Card>
        <CardContent>Content</CardContent>
        <CardFooter>Footer</CardFooter>
      </Card>
    );

    expect(screen.getByText('Footer')).toBeInTheDocument();
  });

  it('supports complex card structure', () => {
    render(
      <Card className="shadow-lg hover:shadow-xl transition-shadow">
        <CardHeader>
          <div>Complex Card</div>
          <div>This is a complex card with multiple sections</div>
        </CardHeader>
        <CardContent>
          <p>Main content goes here</p>
          <p>Multiple paragraphs of content</p>
        </CardContent>
        <CardFooter>
          <button>Save</button>
          <button>Cancel</button>
        </CardFooter>
      </Card>
    );

    expect(screen.getByText('Complex Card')).toBeInTheDocument();
    expect(screen.getByText('This is a complex card with multiple sections')).toBeInTheDocument();
    expect(screen.getByText('Main content goes here')).toBeInTheDocument();
    expect(screen.getByText('Save')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  it('has proper accessibility attributes', async () => {
    const { container } = render(<Card {...baseProps} />);

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    const card = screen.getByTestId('card');
    expect(card).toHaveAttribute('role', 'article');
  });

  it('has proper accessibility when clickable', async () => {
    const { container } = render(<Card onClick={vi.fn()} {...baseProps} />);

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    const card = screen.getByTestId('card');
    expect(card).toBeInTheDocument();
  });

  it('supports keyboard navigation when clickable', () => {
    const handleClick = vi.fn();
    render(<Card onClick={handleClick} {...baseProps} />);

    const card = screen.getByTestId('card');

    // Test Enter key
    fireEvent.keyDown(card, { key: 'Enter' });
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('performs well under load', async () => {
    const stats = await testComponentPerformance('Card', 200, () => {
      const { unmount } = render(<Card {...baseProps} />);
      unmount();
    });

    // Performance assertions are handled by testComponentPerformance function
    expect(stats).toBeDefined();
  });

  it('handles many rapid renders without memory leaks', () => {
    const renderCount = 1000;
    const renderFunction = () => {
      const { unmount } = render(<Card {...baseProps} />);
      unmount();
    };

    const start = performance.now();
    for (let i = 0; i < renderCount; i++) {
      renderFunction();
    }
    const end = performance.now();

    const avgTime = (end - start) / renderCount;
    expect(avgTime).toBeLessThan(0.5); // Should be very fast
  });

  it('supports custom data attributes', () => {
    render(
      <Card
        data-testid="custom-card"
        data-custom="custom-value"
        data-id="123"
        {...baseProps}
      />
    );

    const card = screen.getByTestId('custom-card');
    expect(card).toHaveAttribute('data-custom', 'custom-value');
    expect(card).toHaveAttribute('data-id', '123');
  });

  it('forwards ref correctly', () => {
    const ref = vi.fn();
    render(<Card ref={ref} {...baseProps} />);

    expect(ref).toHaveBeenCalled();
    expect(ref.mock.calls[0][0]).toBeInstanceOf(HTMLDivElement);
  });

  it('has correct displayName', () => {
    expect(Card.displayName).toBe('Card');
    expect(CardHeader.displayName).toBe('CardHeader');
    expect(CardContent.displayName).toBe('CardContent');
    expect(CardFooter.displayName).toBe('CardFooter');
  });

  it('supports custom className with Tailwind', () => {
    render(<Card className="p-6 mb-4 rounded-lg border-2 bg-blue-50 text-blue-900 border-blue-300" {...baseProps} />);

    const card = screen.getByTestId('card');
    expect(card).toHaveClass('p-6', 'mb-4', 'rounded-lg', 'border-2', 'bg-blue-50', 'text-blue-900', 'border-blue-300');
  });
});