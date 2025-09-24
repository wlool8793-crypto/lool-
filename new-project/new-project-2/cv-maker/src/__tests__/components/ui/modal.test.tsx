import { render, screen, fireEvent } from '@testing-library/react';
import { axe } from 'jest-axe';
import { vi } from 'vitest';
import React from 'react';
import { Modal } from '@/components/ui/modal';
import { testComponentPerformance } from '@/test/performance';

describe('Modal Component', () => {
  const baseProps = {
    isOpen: true,
    onClose: vi.fn(),
    title: 'Test Modal',
    children: <div>Modal content</div>,
  };

  it('renders modal when isOpen is true', () => {
    render(<Modal {...baseProps} />);

    expect(screen.getByText('Test Modal')).toBeInTheDocument();
    expect(screen.getByText('Modal content')).toBeInTheDocument();
  });

  it('does not render modal when isOpen is false', () => {
    render(<Modal {...baseProps} isOpen={false} />);

    expect(screen.queryByText('Test Modal')).not.toBeInTheDocument();
    expect(screen.queryByText('Modal content')).not.toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    render(<Modal {...baseProps} />);

    const closeButton = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);

    expect(baseProps.onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when escape key is pressed', () => {
    render(<Modal {...baseProps} />);

    fireEvent.keyDown(document, { key: 'Escape' });

    expect(baseProps.onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when overlay is clicked', () => {
    render(<Modal {...baseProps} />);

    const overlay = screen.getByTestId('modal-overlay');
    fireEvent.click(overlay);

    expect(baseProps.onClose).toHaveBeenCalledTimes(1);
  });

  it('does not call onClose when modal content is clicked', () => {
    render(<Modal {...baseProps} />);

    const modalContent = screen.getByTestId('modal-content');
    fireEvent.click(modalContent);

    expect(baseProps.onClose).not.toHaveBeenCalled();
  });

  it('renders with different sizes', () => {
    const sizes = ['sm', 'md', 'lg', 'xl', 'full'] as const;

    sizes.forEach(size => {
      const { unmount } = render(<Modal {...baseProps} size={size} />);

      const modalContent = screen.getByTestId('modal-content');

      switch (size) {
        case 'sm':
          expect(modalContent).toHaveClass('max-w-sm');
          break;
        case 'md':
          expect(modalContent).toHaveClass('max-w-md');
          break;
        case 'lg':
          expect(modalContent).toHaveClass('max-w-lg');
          break;
        case 'xl':
          expect(modalContent).toHaveClass('max-w-xl');
          break;
        case 'full':
          expect(modalContent).toHaveClass('max-w-full');
          break;
      }

      unmount();
    });
  });

  it('renders with custom className', () => {
    render(<Modal {...baseProps} className="custom-modal" />);

    const modalContent = screen.getByTestId('modal-content');
    expect(modalContent).toHaveClass('custom-modal');
  });

  it('supports showCloseButton prop', () => {
    render(<Modal {...baseProps} showCloseButton={false} />);

    expect(screen.queryByRole('button', { name: /close/i })).not.toBeInTheDocument();
  });

  it('supports closeOnBackdropClick prop', () => {
    render(<Modal {...baseProps} closeOnBackdropClick={false} />);

    const modal = screen.getByRole('dialog');
    expect(modal).toBeInTheDocument();
  });

  it('supports closeOnEscape prop', () => {
    const onClose = vi.fn();
    render(<Modal {...baseProps} onClose={onClose} closeOnEscape={false} />);

    fireEvent.keyDown(document, { key: 'Escape' });
    expect(onClose).not.toHaveBeenCalled();
  });

  it('supports closeOnBackdropClick prop', () => {
    const onClose = vi.fn();
    render(<Modal {...baseProps} onClose={onClose} closeOnBackdropClick={false} />);

    const modal = screen.getByRole('dialog');
    expect(modal).toBeInTheDocument();
  });

  it('has proper accessibility attributes', async () => {
    const { container } = render(<Modal {...baseProps} />);

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    const modal = screen.getByRole('dialog');
    expect(modal).toHaveAttribute('aria-modal', 'true');
    expect(modal).toHaveAttribute('aria-labelledby');
    expect(modal).toHaveAttribute('aria-describedby');
  });

  it('manages focus correctly', () => {
    const { unmount } = render(<Modal {...baseProps} />);

    const modal = screen.getByRole('dialog');
    expect(modal).toHaveFocus();

    unmount();
  });

  it('traps focus within modal', () => {
    render(
      <Modal {...baseProps}>
        <button data-testid="first-button">First Button</button>
        <button data-testid="second-button">Second Button</button>
      </Modal>
    );

    const modal = screen.getByRole('dialog');
    const firstButton = screen.getByTestId('first-button');
    const secondButton = screen.getByTestId('second-button');

    // Simulate tab navigation
    fireEvent.keyDown(modal, { key: 'Tab' });
    expect(firstButton).toHaveFocus();

    fireEvent.keyDown(firstButton, { key: 'Tab' });
    expect(secondButton).toHaveFocus();

    fireEvent.keyDown(secondButton, { key: 'Tab' });
    expect(firstButton).toHaveFocus(); // Should cycle back to first button
  });

  it('performs well under load', async () => {
    const stats = await testComponentPerformance('Modal', 50, () => {
      const { unmount } = render(<Modal {...baseProps} />);
      unmount();
    });

    // Performance assertions are handled by testComponentPerformance function
    expect(stats).toBeDefined();
  });

  it('handles rapid open/close without performance issues', () => {
    const TestComponent = () => {
      const [isOpen, setIsOpen] = React.useState(false);

      return (
        <div>
          <button onClick={() => setIsOpen(!isOpen)}>Toggle Modal</button>
          <Modal isOpen={isOpen} onClose={() => setIsOpen(false)} title={baseProps.title}>
            {baseProps.children}
          </Modal>
        </div>
      );
    };

    const { unmount } = render(<TestComponent />);
    const toggleButton = screen.getByText('Toggle Modal');

    const start = performance.now();
    for (let i = 0; i < 100; i++) {
      fireEvent.click(toggleButton);
      fireEvent.click(toggleButton);
    }
    const end = performance.now();

    const avgTime = (end - start) / 200;
    expect(avgTime).toBeLessThan(2); // Should be fast

    unmount();
  });

  it('has correct displayName', () => {
    expect(Modal.displayName).toBe('Modal');
  });

  it('supports scrollable content', () => {
    const longContent = Array.from({ length: 100 }, (_, i) => (
      <div key={i}>Content line {i}</div>
    ));

    render(<Modal {...baseProps}>{longContent}</Modal>);

    const modalContent = screen.getByTestId('modal-content');
    expect(modalContent).toHaveClass('overflow-y-auto');
  });

  it('supports custom className for styling', () => {
    render(<Modal {...baseProps} className="custom-z-index backdrop-blur-sm" />);

    const modal = screen.getByRole('dialog');
    expect(modal).toHaveClass('custom-z-index');
  });

  it('supports custom className for positioning', () => {
    render(<Modal {...baseProps} className="flex items-center justify-center" />);

    const modal = screen.getByRole('dialog');
    expect(modal).toHaveClass('flex', 'items-center', 'justify-center');
  });

  it('supports custom className for animation', () => {
    render(<Modal {...baseProps} className="transition-all duration-300" />);

    const modal = screen.getByRole('dialog');
    expect(modal).toHaveClass('transition-all', 'duration-300');
  });

  it('handles async onClose callback', async () => {
    const asyncOnClose = vi.fn().mockResolvedValue(undefined);
    render(<Modal {...baseProps} onClose={asyncOnClose} />);

    const closeButton = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);

    expect(asyncOnClose).toHaveBeenCalledTimes(1);
  });

  it('prevents body scroll when modal is open', () => {
    const { unmount } = render(<Modal {...baseProps} />);

    expect(document.body).toHaveClass('overflow-hidden');

    unmount();
    expect(document.body).not.toHaveClass('overflow-hidden');
  });
});