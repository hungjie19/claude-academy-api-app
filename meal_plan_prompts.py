"""第 15-19 堂共用：餐食計畫這個任務的設定與各版本提示。

這五堂是同一個實驗：任務、資料集、評分標準全部固定不動，**每堂只改提示的一件事**，
看平均分往哪裡走。所以這些共用的東西放在這裡，每堂的 script 只負責
「挑一個版本的提示、跑、印出跟上一版的差距」。

每新增一版提示就往下加一個 build_prompt_vN，舊的不要刪——
分數比較要能隨時重跑任一版。
"""

from pathlib import Path

from chat_helpers import add_user_message, chat

DATASET_PATH = Path(__file__).parent / "meal_plan_dataset.json"
REPORT_PATH = Path(__file__).parent / "meal_plan_report.html"

TASK_DESCRIPTION = "Write a compact, concise 1 day meal plan for a single athlete"

PROMPT_INPUTS_SPEC = {
    "height": "Athlete's height in cm",
    "weight": "Athlete's weight in kg",
    "goal": "Goal of the athlete",
    "restrictions": "Dietary restrictions of the athlete",
}

# 資料集的 solution_criteria 是 Claude 自己生的，不一定涵蓋我真正在意的東西，
# 所以這幾項直接告訴評分模型。這也是整個實驗的「及格線」定義。
EXTRA_CRITERIA = """
The output should include:
- Daily caloric total
- Macronutrient breakdown
- Meals with exact foods, portions, and timing
"""


def build_prompt_v1(prompt_inputs):
    """第 15 堂的基準線。刻意寫得很弱：一句問句，什麼要求都沒講。"""
    return f"""
What should this person eat?

- Height: {prompt_inputs["height"]}
- Weight: {prompt_inputs["weight"]}
- Goal: {prompt_inputs["goal"]}
- Dietary restrictions: {prompt_inputs["restrictions"]}
"""


def build_prompt_v2(prompt_inputs):
    """第 16 堂：清晰且直接。只改開頭那一行，其餘一字不動。

    從問句「這個人應該吃什麼？」換成指示句，一句話同時交代三件事：
    要採取的動作（generate）、要產出什麼（meal plan）、關鍵限制
    （一天、運動員、符合飲食限制）。提示的第一行是整個請求裡最重要的部分。
    """
    return f"""
Generate a 1 day meal plan for an athlete that meets their dietary restrictions.

- Height: {prompt_inputs["height"]}
- Weight: {prompt_inputs["weight"]}
- Goal: {prompt_inputs["goal"]}
- Dietary restrictions: {prompt_inputs["restrictions"]}
"""


def build_prompt_v3(prompt_inputs):
    """第 17 堂：具體明確。在 v2 的指示句後面補上輸出品質指引。

    官方分兩種指引：
      1. 輸出品質指引——列出輸出該有的特質（長度、結構、要含哪些元素、語氣）
      2. 流程步驟——要 Claude 照步驟系統性思考，留給複雜的判斷題

    這堂用第一種。重點在「把我沒說但我預期的東西列出來」：
    熱量要準、三大營養素要給、每餐幾點吃、份量用公克。
    這是整組技巧裡分數跳最多的一堂。
    """
    return f"""
Generate a 1 day meal plan for an athlete that meets their dietary restrictions.

- Height: {prompt_inputs["height"]}
- Weight: {prompt_inputs["weight"]}
- Goal: {prompt_inputs["goal"]}
- Dietary restrictions: {prompt_inputs["restrictions"]}

Guidelines:
1. Include accurate daily calorie amount
2. Show protein, fat, and carb amounts
3. Specify when to eat each meal
4. Use only foods that fit restrictions
5. List all portion sizes in grams
6. Keep budget-friendly if mentioned
"""


def runner(build_prompt):
    """把一個 build_prompt_vN 包成 PromptEvaluator 要的 run_prompt_function。"""

    def run_prompt(prompt_inputs):
        messages = []
        add_user_message(messages, build_prompt(prompt_inputs))
        return chat(messages, max_tokens=2000)

    return run_prompt


def ensure_dataset(evaluator, num_cases=3):
    """資料集只生一次就定住。

    每堂重新生資料集的話，分數變化裡混了「換了題目」這個變數，
    2.32 -> 3.92 這種比較就不能用了。
    """
    if DATASET_PATH.exists():
        return
    print(f"{DATASET_PATH.name} 不存在，生成 {num_cases} 筆測試案例...")
    evaluator.generate_dataset(
        task_description=TASK_DESCRIPTION,
        prompt_inputs_spec=PROMPT_INPUTS_SPEC,
        output_file=DATASET_PATH,
        num_cases=num_cases,
    )


def compare(evaluator, versions):
    """同一次執行裡跑多個版本的提示，印出分數與差距，回傳 {label: 平均分}。

    為什麼要重跑舊版、不直接引用上一堂印出來的數字：模型輸出有隨機性，
    跨執行比較等於混進「不同時間跑的」這個變數。要主張「這一招有效」，
    前後兩版就得在同一次執行裡跑。
    """
    from prompt_evaluator import average_score

    averages = {}
    for label, build_prompt in versions.items():
        results = evaluator.run_evaluation(
            run_prompt_function=runner(build_prompt),
            dataset_file=DATASET_PATH,
            extra_criteria=EXTRA_CRITERIA,
            report_file=REPORT_PATH.with_name(f"meal_plan_report_{label}.html"),
        )
        print(f"[{label}]")
        for i, r in enumerate(results, 1):
            inputs = r["test_case"]["prompt_inputs"]
            print(
                f"  {i}. score={r['score']:<5} {inputs['goal']} / {inputs['restrictions']}"
            )
            print(f"     缺點：{'; '.join(r['weaknesses'][:2])}")
        averages[label] = average_score(results)
        print(f"  Average score: {averages[label]:.2f}\n")
    return averages
