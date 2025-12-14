import React from 'react';
import { Users } from 'lucide-react';

export type MealType = 'breakfast' | 'lunch' | 'dinner';

export interface MealToggleProps {
  mealType: MealType;
  isOn: boolean;
  isLocked: boolean;
  guestCount?: number;
  deadlineStatus?: 'safe' | 'warning' | 'critical';
  onToggle: () => void;
  onGuestClick?: () => void;
}

const mealIcons = {
  breakfast: '🌅',
  lunch: '☀️',
  dinner: '🌙',
};

const mealLabels = {
  breakfast: 'B',
  lunch: 'L',
  dinner: 'D',
};

const deadlineColors = {
  safe: 'border-green-500 bg-green-50',
  warning: 'border-yellow-500 bg-yellow-50',
  critical: 'border-red-500 bg-red-50',
};

export const MealToggle: React.FC<MealToggleProps> = ({
  mealType,
  isOn,
  isLocked,
  guestCount = 0,
  deadlineStatus = 'safe',
  onToggle,
  onGuestClick,
}) => {
  const baseClasses = `
    relative flex items-center justify-between gap-2 px-3 py-2 rounded-lg border-2
    transition-all duration-200
    ${isLocked ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:shadow-md'}
  `;

  const stateClasses = isOn
    ? `${deadlineColors[deadlineStatus]} border-opacity-100`
    : 'bg-gray-50 border-gray-200';

  const handleClick = (e: React.MouseEvent) => {
    if (!isLocked) {
      onToggle();
    }
  };

  const handleGuestClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!isLocked && onGuestClick) {
      onGuestClick();
    }
  };

  return (
    <div
      className={`${baseClasses} ${stateClasses}`}
      onClick={handleClick}
      role="button"
      tabIndex={isLocked ? -1 : 0}
      aria-label={`${mealType} - ${isOn ? 'On' : 'Off'}${isLocked ? ' (Locked)' : ''}`}
      aria-pressed={isOn}
      aria-disabled={isLocked}
      onKeyDown={(e) => {
        if ((e.key === 'Enter' || e.key === ' ') && !isLocked) {
          e.preventDefault();
          onToggle();
        }
      }}
    >
      <div className="flex items-center gap-2">
        <span className="text-lg" role="img" aria-label={mealType}>
          {mealIcons[mealType]}
        </span>
        <span className="font-semibold text-xs uppercase tracking-wide text-gray-700">
          {mealLabels[mealType]}
        </span>
      </div>

      <div className="flex items-center gap-2">
        {/* Toggle Switch */}
        <div
          className={`
            relative inline-flex h-5 w-9 items-center rounded-full transition-colors
            ${isOn ? 'bg-green-500' : 'bg-gray-300'}
            ${isLocked ? 'opacity-60' : ''}
          `}
        >
          <span
            className={`
              inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition-transform
              ${isOn ? 'translate-x-5' : 'translate-x-0.5'}
            `}
          />
        </div>

        {/* Guest Counter */}
        {guestCount > 0 && (
          <button
            onClick={handleGuestClick}
            disabled={isLocked}
            className={`
              flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium
              bg-blue-100 text-blue-700 hover:bg-blue-200
              ${isLocked ? 'opacity-60 cursor-not-allowed' : ''}
            `}
            title="Guest meals"
            aria-label={`${guestCount} guest meals`}
          >
            <Users className="w-3 h-3" />
            <span>{guestCount}</span>
          </button>
        )}
      </div>

      {/* Locked Indicator */}
      {isLocked && (
        <div className="absolute -top-1 -right-1 w-4 h-4 bg-gray-600 rounded-full flex items-center justify-center">
          <span className="text-white text-xs">🔒</span>
        </div>
      )}
    </div>
  );
};

export default MealToggle;
