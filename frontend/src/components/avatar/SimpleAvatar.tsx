import React from 'react';

interface SimpleAvatarProps {
  imageUrl: string;
  name?: string;
  size?: 'small' | 'medium' | 'large';
  className?: string;
  showName?: boolean;
}

const SimpleAvatar: React.FC<SimpleAvatarProps> = ({ 
  imageUrl, 
  name, 
  size = 'medium', 
  className = '',
  showName = false 
}) => {
  const sizeClasses = {
    small: 'w-12 h-12',
    medium: 'w-16 h-16',
    large: 'w-24 h-24'
  };

  return (
    <div className={`flex flex-col items-center ${className}`}>
      <div className={`${sizeClasses[size]} rounded-full overflow-hidden bg-gray-100 border-2 border-gray-200`}>
        <img 
          src={imageUrl} 
          alt={name || 'Avatar'} 
          className="w-full h-full object-cover"
          onError={(e) => {
            // Fallback en caso de error
            e.currentTarget.src = '/default-avatar.png';
          }}
        />
      </div>
      {showName && name && (
        <span className="mt-1 text-sm text-gray-700 text-center">{name}</span>
      )}
    </div>
  );
};

export default SimpleAvatar;