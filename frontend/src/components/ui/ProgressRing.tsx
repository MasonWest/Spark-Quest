import type { FC } from "react";

interface Props {
  percentage: number;
  size?: number;
  strokeWidth?: number;
  showLabel?: boolean;
  className?: string;
  "aria-label"?: string;
}

const ProgressRing: FC<Props> = ({
  percentage,
  size = 64,
  strokeWidth = 6,
  showLabel = false,
  className = "",
  "aria-label": ariaLabel,
}) => {
  const center = size / 2;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - Math.max(0, Math.min(100, percentage)) / 100);
  // 只旋转「弧」本身，让进度从 12 点方向起算；SVG 与中心文字都不旋转。
  const arcRotation = `rotate(-90 ${center} ${center})`;

  return (
    <svg
      className={`progress-ring ${className}`}
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      role="img"
      aria-label={ariaLabel}
      style={{ "--size": `${size}px`, "--stroke": strokeWidth, "--dash": circumference, "--offset": offset } as React.CSSProperties}
    >
      <circle
        className="progress-ring__bg"
        cx={center}
        cy={center}
        r={radius}
        fill="none"
        transform={arcRotation}
      />
      <circle
        className="progress-ring__fg"
        cx={center}
        cy={center}
        r={radius}
        fill="none"
        strokeLinecap="round"
        transform={arcRotation}
      />
      {showLabel && (
        <text
          className="progress-ring__label"
          x={center}
          y={center}
          textAnchor="middle"
          dominantBaseline="central"
          fontSize={size * 0.22}
          fontWeight={700}
          fill="var(--sq-text)"
          fontFamily="system-ui, -apple-system, Segoe UI, sans-serif"
        >
          {Math.round(percentage)}%
        </text>
      )}
    </svg>
  );
};

export default ProgressRing;
