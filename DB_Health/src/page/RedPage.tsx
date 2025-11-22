import styles from "./RedPage.module.css";
import AttendanceGrid from "../commponent/RedPageCommponent/AttendanceGrid";

const RedPage = () => {
  return (
    <section className={styles.wrapper}>
      <div className={styles.content}>
        <AttendanceGrid />
      </div>
    </section>
  );
};

export default RedPage;