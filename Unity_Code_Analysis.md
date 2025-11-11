# Infinite Stairs - Unity 코드 분석

무한의계단 게임의 Unity 코드 구조와 각 스크립트의 역할

## 스크립트 목록

## GameManager.cs
게임의 메인 로직 관리

- 계단 20개를 순환적으로 생성/재사용
- 점수, 게이지, 게임오버 상태 관리
- 플레이어 입력 처리 (올라가기/방향전환)
- BGM, 사운드, 진동 설정 제어

주요 메서드:
- `StairsInit()` - 게임 시작시 계단 배치
- `StairMove()` - 계단 이동 처리
- `GaugeReduce()` - 시간에 따른 게이지 감소
- `GameOver()` - 게임오버 처리

게임 상태: start, leftDir, rightDir

## Player.cs
플레이어 캐릭터 제어

- `Climb()` - 계단 오르기 및 방향 전환
- `MoveAnimation()` - 이동 및 대기 애니메이션
- 코인 수집 (OnTriggerEnter2D)
- 방향에 따른 캐릭터 회전

주요 변수: isleft, isDie, stairIndex, money

## DSLManager.cs
데이터 저장/로드 시스템

- JSON 직렬화 + Base64 암호화 저장
- 7개 캐릭터 구매/선택 상태 관리
- 랭킹 시스템 (최고점수 4개 저장)
- BGM, 사운드, 진동 설정 저장

데이터 클래스:
- `Character` - 캐릭터 정보 (이름, 가격, 구매/선택 상태)
- `Ranking` - 점수와 캐릭터 인덱스
- `Inform` - 게임 설정 (돈, BGM, 사운드, 진동, 재시작)

## CharacterManager.cs
캐릭터 선택 UI 관리

- 캐릭터 정보 표시 (이름, 가격, 이미지)
- 좌우 화살표로 캐릭터 순환 선택
- 구매/선택 버튼 전환

캐릭터: 회사원, 래퍼, 비서, 복서, 치어리더, 보안관, 배관공

## ObjectManager.cs
오브젝트 풀링 시스템

- 20개 코인 오브젝트 미리 생성 및 재사용
- 필요시 오브젝트 활성화/비활성화
- 런타임 메모리 할당 최소화

## DontDestory.cs
BGM 관리 (싱글톤)

- DontDestroyOnLoad로 씬 전환시에도 BGM 유지
- 설정에 따른 배경음악 재생/정지

## 게임 구조

### 계단 시스템
- 20개 계단 순환 재사용
- 33% 확률로 방향 변경
- 33% 확률로 코인 생성

### 점수 시스템  
- 계단당 1점
- 시간제한 게이지
- 점수별 난이도 증가

### 캐릭터 시스템
- 7개 캐릭터 (가격: 0~2000 코인)
- 코인으로 구매
- 선택 상태 저장

### 데이터 저장
- JSON + Base64 암호화
- Application.persistentDataPath
- 캐릭터, 랭킹, 설정 정보

## 기술 특징

- 오브젝트 풀링으로 메모리 최적화
- 싱글톤 패턴으로 BGM 관리
- 코루틴으로 비동기 처리
- 모바일 최적화 (터치, 진동)

---

# 기능별 함수 매핑 가이드

## 1. 게임 핵심 로직

### 계단 시스템
- **계단 초기 생성**: `Assets/Scripts/GameManager.cs:50` → `StairsInit()`
- **계단 재배치**: `Assets/Scripts/GameManager.cs:82` → `SpawnStair(int num)`
- **계단 이동 처리**: `Assets/Scripts/GameManager.cs:106` → `StairMove(int stairIndex, bool isChange, bool isleft)`

### 플레이어 제어
- **계단 오르기/방향전환**: `Assets/Scripts/Player.cs:19` → `Climb(bool isChange)`
- **캐릭터 애니메이션**: `Assets/Scripts/Player.cs:29` → `MoveAnimation()`, `Assets/Scripts/Player.cs:43` → `IdleAnimation()`
- **코인 수집**: `Assets/Scripts/Player.cs:49` → `OnTriggerEnter2D(Collider2D collision)`

### 게이지 시스템
- **게이지 감소**: `Assets/Scripts/GameManager.cs:134` → `GaugeReduce()`
- **게이지 체크**: `Assets/Scripts/GameManager.cs:150` → `CheckGauge()` (코루틴)
- **게임오버 처리**: `Assets/Scripts/GameManager.cs:158` → `GameOver()`
- **점수 표시**: `Assets/Scripts/GameManager.cs:178` → `ShowScore()`

## 2. 데이터 관리

### 캐릭터 관리
- **캐릭터 선택 저장**: `Assets/Scripts/DSLManager.cs:132` → `SaveCharacterIndex()`
- **선택된 캐릭터 조회**: `Assets/Scripts/DSLManager.cs:140` → `GetSelectedCharIndex()`
- **캐릭터 구매 여부 확인**: `Assets/Scripts/DSLManager.cs:151` → `IsPurchased(int index)`
- **캐릭터 구매 처리**: `Assets/Scripts/DSLManager.cs:156` → `SaveCharacterPurchased(Animator obj)`
- **캐릭터 가격 조회**: `Assets/Scripts/DSLManager.cs:171` → `GetPrice()`

### 코인/돈 관리
- **코인 조회**: `Assets/Scripts/DSLManager.cs:178` → `GetMoney()`
- **코인 저장**: `Assets/Scripts/DSLManager.cs:183` → `SaveMoney(int money)`
- **UI 코인 업데이트**: `Assets/Scripts/DSLManager.cs:190` → `LoadMoney(int money)`

### 랭킹 관리
- **랭킹 UI 로드**: `Assets/Scripts/DSLManager.cs:213` → `LoadRanking()`
- **점수 저장 및 정렬**: `Assets/Scripts/DSLManager.cs:220` → `SaveRankScore(int finalScore)`
- **최고점수 조회**: `Assets/Scripts/DSLManager.cs:235` → `GetBestScore()`

### 설정 관리
- **설정 상태 조회**: `Assets/Scripts/DSLManager.cs:244` → `GetSettingOn(string type)`
- **설정 토글**: `Assets/Scripts/DSLManager.cs:257` → `ChangeOnOff(Button btn)`

### 재시작 관리
- **재시작 모드 확인**: `Assets/Scripts/DSLManager.cs:201` → `IsRetry()`
- **재시작 상태 변경**: `Assets/Scripts/DSLManager.cs:203` → `ChangeRetry(bool isRetry)`

### 핵심 데이터 처리
- **데이터 저장**: `Assets/Scripts/DSLManager.cs:90` → `DataSave()` (JSON + Base64 암호화)
- **데이터 로드**: `Assets/Scripts/DSLManager.cs:109` → `DataLoad()` (복호화 + 역직렬화)
- **JSON 직렬화**: `Assets/JsonDotNet/Assemblies/Standalone/Newtonsoft.Json.dll` → JsonConvert 클래스 사용

## 3. UI 및 입력 처리

### 버튼 피드백
- **버튼 누름 효과**: `Assets/Scripts/GameManager.cs:190` → `BtnDown(GameObject btn)`
- **버튼 놓음 효과**: `Assets/Scripts/GameManager.cs:197` → `BtnUp(GameObject btn)`
- **씬 전환**: `Assets/Scripts/GameManager.cs:298` → `LoadScene(int i)`

### 사운드 관리
- **사운드 재생**: `Assets/Scripts/GameManager.cs:288` → `PlaySound(int index)`
- **사운드 초기화**: `Assets/Scripts/GameManager.cs:212` → `SoundInit()`
- **설정 버튼 초기화**: `Assets/Scripts/GameManager.cs:221` → `SettingBtnInit()`
- **설정 적용**: `Assets/Scripts/GameManager.cs:264` → `SettingOnOff(string type)`, `Assets/Scripts/GameManager.cs:243` → `SettingBtnChange(Button btn)`

## 4. 캐릭터 선택 시스템

### 캐릭터 순환
- **좌우 화살표 처리**: `Assets/Scripts/CharacterManager.cs:25` → `ArrowBtn(string dir)`
- **캐릭터 정보 업데이트**: `Assets/Scripts/CharacterManager.cs:34-36` → 이미지, 이름, 가격 자동 갱신
- **구매/선택 버튼 전환**: `Assets/Scripts/CharacterManager.cs:39-40` → 구매 상태에 따른 버튼 표시

## 5. 오브젝트 관리

### 코인 시스템
- **코인 풀 생성**: `Assets/Scripts/ObjectManager.cs:19` → `Generate()`
- **코인 활성화**: `Assets/Scripts/ObjectManager.cs:30` → `MakeObj(string type, int index)`
- **코인 프리팹**: `Assets/Prefabs/Coin.prefab` → 오브젝트 풀링 대상

### BGM 관리 (싱글톤)
- **BGM 재생**: `Assets/Scripts/DontDestory.cs:20` → `BgmPlay()`
- **BGM 정지**: `Assets/Scripts/DontDestory.cs:28` → `BgmStop()`
- **싱글톤 패턴**: `Assets/Scripts/DontDestory.cs:11` → `Awake()` 중복 생성 방지

## 6. 리소스 및 에셋

### 애니메이션
- **캐릭터 애니메이션**: `Assets/Animations/1.BusinessMan/` ~ `Assets/Animations/7.Plumber/`
- **Move 애니메이션**: 각 캐릭터별 `BusinessManMove.anim`, `RapperMove.anim` 등
- **Die 애니메이션**: 각 캐릭터별 `BusinessManDie.anim`, `RapperDie.anim` 등
- **UI 애니메이션**: `Assets/Animations/GameOver.anim`, `Assets/Animations/BestScore.anim`

### 사운드
- **배경음악**: `Assets/Audio/무한의계단 bgm 1.mp3`
- **효과음**: `Assets/Audio/DM-CGS-*.wav`, `Assets/Audio/456693__combine2005__pickup-coin56.wav`
- **게임오버**: `Assets/Audio/게임오버.MP3`

### 스프라이트 및 이미지
- **캐릭터**: `Assets/Sprites/무한의계단 캐릭터들.PNG`
- **UI 요소**: `Assets/Sprites/UI_Button.png`, `Assets/Sprites/방향전환버튼.PNG`
- **배경**: `Assets/Sprites/bg001.png`, `Assets/Sprites/계단.PNG`

### 폰트
- **게임 폰트**: `Assets/Fonts/CookieRun Black.ttf`, `Assets/Fonts/FlappyFont.TTF`

### 씬 구조
- **메인 게임**: `Assets/Scenes/GameStart.unity`
- **캐릭터 선택**: `Assets/Scenes/Character.unity`

## 7. 핵심 코드 구조

### 게임 초기화 순서
```csharp
// Assets/Scripts/DSLManager.cs:58-87 (Awake)
DataLoad() → LoadMoney() → LoadRanking() → SettingBtnInit()

// Assets/Scripts/GameManager.cs:36-46 (Awake)  
StairsInit() → GaugeReduce() → CheckGauge()

// Assets/Scripts/Player.cs:14-17 (Awake)
anim = GetComponent<Animator>() → money = dslManager.GetMoney()
```

### 게임플레이 루프
```csharp
// 버튼 입력: Assets/Scripts/GameManager.cs:190-207
BtnDown() → Player.Climb() → StairMove() → 점수증가/게이지증가

// 게이지 시스템: Assets/Scripts/GameManager.cs:134-155
GaugeReduce() (0.01초마다) → CheckGauge() (0.4초마다) → GameOver()
```

### 데이터 저장 흐름
```csharp
// Assets/Scripts/DSLManager.cs:90-105 (저장)
JsonConvert.SerializeObject() → UTF8.GetBytes() → Base64String() → File.WriteAllText()

// Assets/Scripts/DSLManager.cs:109-125 (로드)  
File.ReadAllText() → FromBase64String() → UTF8.GetString() → JsonConvert.DeserializeObject()
```

### 저장 위치
- **JSON 데이터**: `Application.persistentDataPath/Characters.json`, `/Rankings.json`, `/Informs.json`
- **암호화**: Base64 인코딩으로 기본 보안 적용