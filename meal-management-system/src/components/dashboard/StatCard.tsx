import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
    label?: string;
  };
  description?: string;
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple' | 'indigo';
  onClick?: () => void;
}

const colorClasses = {
  blue: {
    bg: 'bg-blue-50',
    icon: 'text-blue-600',
    trend: 'text-blue-600',
  },
  green: {
    bg: 'bg-green-50',
    icon: 'text-green-600',
    trend: 'text-green-600',
  },
  yellow: {
    bg: 'bg-yellow-50',
    icon: 'text-yellow-600',
    trend: 'text-yellow-600',
  },
  red: {
    bg: 'bg-red-50',
    icon: 'text-red-600',
    trend: 'text-red-600',
  },
  purple: {
    bg: 'bg-purple-50',
    icon: 'text-purple-600',
    trend: 'text-purple-600',
  },
  indigo: {
    bg: 'bg-indigo-50',
    icon: 'text-indigo-600',
    trend: 'text-indigo-600',
  },
};

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon: Icon,
  trend,
  description,
  color = 'blue',
  onClick,
}) => {
  const colors = colorClasses[color];
  const isClickable = !!onClick;

  return (
    <div
      onClick={onClick}
      className={`
        bg-white rounded-lg border border-gray-200 p-6
        transition-all duration-200
        ${isClickable ? 'cursor-pointer hover:shadow-md hover:border-gray-300' : ''}
      `}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mb-2">{value}</p>

          {trend && (
            <div className="flex items-center gap-1 mb-2">
              {trend.isPositive ? (
                <TrendingUp className="w-4 h-4 text-green-600" />
              ) : (
                <TrendingDown className="w-4 h-4 text-red-600" />
              )}
              <span
                className={`text-sm font-medium ${
                  trend.isPositive ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {trend.value > 0 ? '+' : ''}
                {trend.value}%
              </span>
              {trend.label && (
                <span className="text-sm text-gray-500 ml-1">{trend.label}</span>
              )}
            </div>
          )}

          {description && (
            <p className="text-sm text-gray-500">{description}</p>
          )}
        </div>

        <div className={`${colors.bg} rounded-lg p-3`}>
          <Icon className={`w-6 h-6 ${colors.icon}`} />
        </div>
      </div>
    </div>
  );
};

export default StatCard;
