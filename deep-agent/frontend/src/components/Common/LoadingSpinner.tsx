import React from 'react';
import { Spinner, Box } from '@chakra-ui/react';

interface LoadingSpinnerProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  color?: string;
  thickness?: string;
  speed?: string;
  emptyColor?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  color = 'blue.500',
  thickness = '2px',
  speed = '0.65s',
  emptyColor = 'transparent',
}) => {
  const sizeMap = {
    xs: '20px',
    sm: '24px',
    md: '32px',
    lg: '48px',
    xl: '64px',
  };

  return (
    <Box display="flex" alignItems="center" justifyContent="center">
      <Spinner
        size={size}
        color={color}
        thickness={thickness}
        speed={speed}
        emptyColor={emptyColor}
        className="spin"
      />
    </Box>
  );
};

export default LoadingSpinner;