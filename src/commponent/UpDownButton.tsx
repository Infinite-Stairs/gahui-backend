import styles from "./UpDownButton.module.css";
import 빨강 from "../assets/빨강.png";
import 파랑 from "../assets/파랑.png";

const UpDownButton = () =>{
    return (
        <>
        <div className={styles.RedButton}>
        <img src={빨강} alt="빨강버튼" width={200} />
        </div>
        <div className={styles.BludButton}>
        <img src={파랑} alt="파랑버튼" width={200} />
        </div>
</>
    );
}

export default UpDownButton;