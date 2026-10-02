import pandas as pd
import ast
import os

def process_marketing_data(posts_path, game_name):
    print(f"正在處理 {game_name} 的數據...")
    # 讀取資料，low_memory=False 避免型別警告
    df = pd.read_csv(posts_path, low_memory=False)
    
    # 轉換時間並過濾無效值
    df['時間'] = pd.to_datetime(df['時間'], errors='coerce')
    df = df.dropna(subset=['時間'])
    df['Month'] = df['時間'].dt.to_period('M')
    
    # 用於存儲每月數據的清單
    monthly_data = []
    
    # 總體推噓統計
    total_p = 0
    total_n = 0

    for _, row in df.iterrows():
        p_count = 0
        n_count = 0
        try:
            # 解析字串格式的留言清單
            comments = ast.literal_eval(row['留言內容'])
            for c in comments:
                if c['type'] == '推':
                    p_count += 1
                elif c['type'] == '噓':
                    n_count += 1
        except:
            pass
        
        total_p += p_count
        total_n += n_count
        monthly_data.append({
            'Month': row['Month'],
            'Posts': 1,
            'P': p_count,
            'N': n_count
        })

    # 建立 DataFrame 並按月彙整
    monthly_df = pd.DataFrame(monthly_data)
    summary = monthly_df.groupby('Month').agg({
        'Posts': 'sum',
        'P': 'sum',
        'N': 'sum'
    })
    
    # 計算情緒分數 (P-N)/(P+N)
    summary['Sentiment_Score'] = (summary['P'] - summary['N']) / (summary['P'] + summary['N']).replace(0, 1)
    
    return {
        'total_p': total_p,
        'total_n': total_n,
        'trend': summary
    }

# 檔案路徑
p_pikmin = "ppt pikmin/ptt_pikmin_202105_202605.csv"
p_pokemon = "ppt pokemon/ptt_pokemon_go_202105_202605.csv"

# 執行整合分析
pikmin_results = process_marketing_data(p_pikmin, "Pikmin Bloom")
pokemon_results = process_marketing_data(p_pokemon, "Pokemon GO")

# --- 產出結果 ---

print("\n" + "="*30)
print("1. 各品牌總體情緒對照 (長條圖用數據)")
print("="*30)
print(f"Pikmin Bloom: 推(P)={pikmin_results['total_p']}, 噓(N)={pikmin_results['total_n']}, P/N比={round(pikmin_results['total_p']/(pikmin_results['total_n'] or 1), 2)}")
print(f"Pokemon GO:   推(P)={pokemon_results['total_p']}, 噓(N)={pokemon_results['total_n']}, P/N比={round(pokemon_results['total_p']/(pokemon_results['total_n'] or 1), 2)}")

print("\n" + "="*30)
print("2. 每月熱度與情緒趨勢 (折線圖用數據 - 最近12個月)")
print("="*30)
print("\n[Pikmin Bloom 趨勢]")
print(pikmin_results['trend'].tail(12))
print("\n[Pokemon GO 趨勢]")
print(pokemon_results['trend'].tail(12))

# 匯出成 CSV 
pikmin_results['trend'].to_csv("pikmin_marketing_summary.csv", encoding="utf-8-sig")
pokemon_results['trend'].to_csv("pokemon_marketing_summary.csv", encoding="utf-8-sig")

print("\n已產出彙整檔案: pikmin_marketing_summary.csv, pokemon_marketing_summary.csv")
