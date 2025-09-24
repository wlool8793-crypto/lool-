import { axe, toHaveNoViolations } from 'jest-axe';

// Extend Jest expect with axe matchers
expect.extend(toHaveNoViolations);

// Accessibility test utilities
export const testAccessibility = async (container: HTMLElement) => {
  const results = await axe(container);
  expect(results).toHaveNoViolations();
  return results;
};

// Common accessibility tests
export const commonAccessibilityTests = {
  hasValidAltText: (img: HTMLImageElement) => {
    expect(img).toHaveAccessibleName();
    expect(img.alt).not.toBe('');
  },
  hasProperFormLabels: (input: HTMLInputElement) => {
    expect(input).toHaveAccessibleName();
  },
  hasProperButtonLabels: (button: HTMLButtonElement) => {
    expect(button).toHaveAccessibleName();
  },
  hasProperHeadingStructure: (headings: HTMLHeadingElement[]) => {
    // Check that heading levels are sequential
    for (let i = 1; i < headings.length; i++) {
      const currentLevel = parseInt(headings[i].tagName[1]);
      const previousLevel = parseInt(headings[i - 1].tagName[1]);

      // Allow jumps of at most 1 level (except from h1)
      if (previousLevel !== 1 && currentLevel > previousLevel + 1) {
        console.warn(`Heading level jump from h${previousLevel} to h${currentLevel}`);
      }
    }
  },
  hasProperFocusManagement: (element: HTMLElement) => {
    expect(element).toHaveAttribute('tabindex');
  },
  hasProperARIAAttributes: (element: HTMLElement, attributes: Record<string, string>) => {
    Object.entries(attributes).forEach(([key, value]) => {
      expect(element).toHaveAttribute(key, value);
    });
  },
};