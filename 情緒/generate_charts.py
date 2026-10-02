import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# 嘗試設定中文字型 (Windows 常用字型)
try:
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
except:
    print("無法設定中文字型，圖表可能顯示為亂碼。")

def load_data():
    pikmin_df = pd.read_csv('pikmin_marketing_summary.csv')
    pokemon_df = pd.read_csv('pokemon_marketing_summary.csv')
    
    # 轉換 Month 為 datetime 以便排序和繪圖
    pikmin_df['Month'] = pd.to_datetime(pikmin_df['Month'])
    pokemon_df['Month'] = pd.to_datetime(pokemon_df['Month'])
    
    return pikmin_df, pokemon_df

def plot_brand_sentiment(pikmin_df, pokemon_df):
    print("正在繪製品牌情緒長條圖...")
    pikmin_p = pikmin_df['P'].sum()
    pikmin_n = pikmin_df['N'].sum()
    pokemon_p = pokemon_df['P'].sum()
    pokemon_n = pokemon_df['N'].sum()
    
    labels = ['Pikmin Bloom', 'Pokemon GO']
    p_counts = [pikmin_p, pokemon_p]
    n_counts = [pikmin_n, pokemon_n]
    
    x = range(len(labels))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar([i - width/2 for i in x], p_counts, width, label='正面 (P)', color='skyblue')
    rects2 = ax.bar([i + width/2 for i in x], n_counts, width, label='負面 (N)', color='salmon')
    
    ax.set_ylabel('評論數')
    ax.set_title('品牌總體情緒對比 (P vs N)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    
    # 加入數值標籤
    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    
    plt.tight_layout()
    plt.savefig('brand_sentiment_bar.png')
    plt.close()

def plot_discussion_volume(pikmin_df, pokemon_df):
    print("正在繪製討論量折線圖...")
    plt.figure(figsize=(12, 6))
    
    plt.plot(pikmin_df['Month'], pikmin_df['Posts'], marker='o', label='Pikmin Bloom')
    plt.plot(pokemon_df['Month'], pokemon_df['Posts'], marker='s', label='Pokemon GO')
    
    plt.title('品牌討論量趨勢 (月文章數)')
    plt.xlabel('時間')
    plt.ylabel('文章篇數')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig('discussion_volume_line.png')
    plt.close()

def plot_sentiment_trend(pikmin_df, pokemon_df):
    print("正在繪製情緒趨勢折線圖...")
    plt.figure(figsize=(12, 6))
    
    plt.plot(pikmin_df['Month'], pikmin_df['Sentiment_Score'], marker='o', label='Pikmin Bloom')
    plt.plot(pokemon_df['Month'], pokemon_df['Sentiment_Score'], marker='s', label='Pokemon GO')
    
    plt.title('情緒分數趨勢 (-1 到 1)')
    plt.xlabel('時間')
    plt.ylabel('情緒分數')
    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig('sentiment_trend_line.png')
    plt.close()

def plot_brand_positioning(pikmin_df, pokemon_df):
    print("正在繪製品牌定位散佈圖...")
    # 計算各品牌的平均聲量與平均情緒
    pikmin_avg_vol = pikmin_df['Posts'].mean()
    pikmin_avg_sent = pikmin_df['Sentiment_Score'].mean()
    pokemon_avg_vol = pokemon_df['Posts'].mean()
    pokemon_avg_sent = pokemon_df['Sentiment_Score'].mean()
    
    plt.figure(figsize=(10, 8))
    
    # 繪製散佈點
    plt.scatter(pikmin_avg_vol, pikmin_avg_sent, s=1000, color='skyblue', alpha=0.7, label='Pikmin Bloom')
    plt.scatter(pokemon_avg_vol, pokemon_avg_sent, s=1000, color='orange', alpha=0.7, label='Pokemon GO')
    
    # 加入標籤
    plt.text(pikmin_avg_vol, pikmin_avg_sent, ' Pikmin', fontsize=12, fontweight='bold', va='center')
    plt.text(pokemon_avg_vol, pokemon_avg_sent, ' Pokemon GO', fontsize=12, fontweight='bold', va='center')
    
    plt.title('品牌定位分析：聲量 vs. 情緒')
    plt.xlabel('平均每月討論量 (聲量)')
    plt.ylabel('平均情緒分數 (好感度)')
    
    # 設定坐標軸範圍與參考線
    plt.axhline(0.8, color='gray', linestyle='--', alpha=0.5) # 假設 0.8 以上為極佳
    plt.grid(True, linestyle=':', alpha=0.6)
    
    # 象限說明文字
    plt.text(plt.xlim()[0]+1, 0.95, '高品質/小眾', fontsize=10, color='gray')
    plt.text(plt.xlim()[1]-15, 0.95, '市場領導者', fontsize=10, color='gray')

    plt.legend()
    plt.tight_layout()
    plt.savefig('brand_positioning_scatter.png')
    plt.close()

if __name__ == "__main__":
    if not os.path.exists('pikmin_marketing_summary.csv') or not os.path.exists('pokemon_marketing_summary.csv'):
        print("錯誤: 找不到 CSV 檔案。請先執行 integrated_marketing_analysis.py")
    else:
        p_df, m_df = load_data()
        plot_brand_sentiment(p_df, m_df)
        plot_discussion_volume(p_df, m_df)
        plot_sentiment_trend(p_df, m_df)
        plot_brand_positioning(p_df, m_df)
        print("所有圖表已成功產出: brand_sentiment_bar.png, discussion_volume_line.png, sentiment_trend_line.png, brand_positioning_scatter.png")
