import React, { useState } from "react";
import styles from "./AttendanceGrid.module.css";
import { AttendanceGridDummy } from "../../data/AttendanceGridDummy";

interface DayData {
  date: string;
  stepCount: number;
}

const AttendanceGrid: React.FC = () => {
  const [hoverInfo, setHoverInfo] = useState<DayData | null>(null);
  const days = AttendanceGridDummy;

  const getColorLevel = (steps: number): string => {
    if (steps === 0) return "level-0";
    if (steps < 10) return "level-1";
    if (steps < 20) return "level-2";
    if (steps < 40) return "level-3";
    return "level-4";
  };

  return (
    <div className={styles.attendancContainer}>
      <div className={styles.attendanceGrid}>
        {days.map((day) => (
          <div
            key={day.date}
            className={`cell ${getColorLevel(day.stepCount)}`}
            onMouseEnter={() => setHoverInfo(day)}
            onMouseLeave={() => setHoverInfo(null)}
          />
        ))}
      </div>

      {hoverInfo && (
        <div className={styles.tooltip}>
          <p>{hoverInfo.date}</p>
          <p>계단 수: {hoverInfo.stepCount}</p>
        </div>
      )}
    </div>
  );
};

export default AttendanceGrid;
