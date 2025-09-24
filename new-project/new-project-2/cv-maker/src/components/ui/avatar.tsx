import * as React from 'react';
import { cn } from '@/lib/utils';
import { User, Camera } from 'lucide-react';

export interface AvatarProps {
  src?: string;
  alt?: string;
  fallback?: React.ReactNode;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  shape?: 'circle' | 'square' | 'rounded';
  className?: string;
  status?: 'online' | 'offline' | 'away' | 'busy';
  showEditButton?: boolean;
  onEditClick?: () => void;
}

const sizeClasses = {
  xs: 'w-6 h-6 text-xs',
  sm: 'w-8 h-8 text-sm',
  md: 'w-10 h-10 text-base',
  lg: 'w-12 h-12 text-lg',
  xl: 'w-16 h-16 text-xl',
  '2xl': 'w-24 h-24 text-2xl',
};

const statusClasses = {
  online: 'bg-green-500',
  offline: 'bg-gray-400',
  away: 'bg-yellow-500',
  busy: 'bg-red-500',
};

const shapeClasses = {
  circle: 'rounded-full',
  square: 'rounded-none',
  rounded: 'rounded-lg',
};

const Avatar: React.FC<AvatarProps> = ({
  src,
  alt,
  fallback,
  size = 'md',
  shape = 'circle',
  className,
  status,
  showEditButton = false,
  onEditClick,
}) => {
  const [imageError, setImageError] = React.useState(false);

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0).toUpperCase())
      .slice(0, 2)
      .join('');
  };

  const renderFallback = () => {
    if (fallback) {
      return <div className="w-full h-full flex items-center justify-center">{fallback}</div>;
    }

    if (alt) {
      return (
        <div className="w-full h-full flex items-center justify-center bg-secondary-200 text-secondary-600 font-medium">
          {getInitials(alt)}
        </div>
      );
    }

    return (
      <div className="w-full h-full flex items-center justify-center bg-secondary-200 text-secondary-600">
        <User className="w-1/2 h-1/2" />
      </div>
    );
  };

  return (
    <div className={cn('relative inline-block', sizeClasses[size], className)}>
      <div
        className={cn(
          'w-full h-full overflow-hidden bg-secondary-200 border-2 border-background',
          shapeClasses[shape]
        )}
      >
        {src && !imageError ? (
          <img
            src={src}
            alt={alt || 'Avatar'}
            className="w-full h-full object-cover"
            onError={() => setImageError(true)}
          />
        ) : (
          renderFallback()
        )}
      </div>

      {status && (
        <div
          className={cn(
            'absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-background',
            statusClasses[status]
          )}
        />
      )}

      {showEditButton && (
        <button
          onClick={onEditClick}
          className="absolute inset-0 w-full h-full flex items-center justify-center bg-black/50 opacity-0 hover:opacity-100 transition-opacity rounded-full"
          aria-label="Edit avatar"
        >
          <Camera className="w-5 h-5 text-white" />
        </button>
      )}
    </div>
  );
};

// Avatar Group component
export interface AvatarGroupProps {
  avatars: AvatarProps[];
  max?: number;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  className?: string;
  showCount?: boolean;
}

const AvatarGroup: React.FC<AvatarGroupProps> = ({
  avatars,
  max = 3,
  size = 'md',
  className,
  showCount = true,
}) => {
  const visibleAvatars = avatars.slice(0, max);
  const remainingCount = avatars.length - max;

  return (
    <div className={cn('flex -space-x-2', className)}>
      {visibleAvatars.map((avatar, index) => (
        <Avatar
          key={index}
          {...avatar}
          size={size}
          className="border-2 border-background"
        />
      ))}
      {showCount && remainingCount > 0 && (
        <div
          className={cn(
            'flex items-center justify-center bg-secondary-200 text-secondary-600 font-medium border-2 border-background',
            sizeClasses[size],
            shapeClasses.circle
          )}
        >
          +{remainingCount}
        </div>
      )}
    </div>
  );
};

export { Avatar, AvatarGroup };