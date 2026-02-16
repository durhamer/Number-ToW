import streamlit as st

# --- 1. 穩健的初始化機制 ---
if 'game_started' not in st.session_state:
    st.session_state.rope_pos = 0
    st.session_state.p1_hand = [1, 2, 3, 4, 5, 0]
    st.session_state.p2_hand = [1, 2, 3, 4, 5, 0]
    st.session_state.p1_name = ""  # 玩家 1 名字
    st.session_state.p2_name = ""  # 玩家 2 名字
    st.session_state.current_turn_name = "" 
    st.session_state.p1_choice = None
    st.session_state.last_result = "遊戲開始！"
    st.session_state.phase = "setup" # 新增 setup 階段
    st.session_state.p1_visible_hand_for_p2 = [1, 2, 3, 4, 5, 0]
    st.session_state.game_started = True

st.set_page_config(page_title="數字拔河博弈", layout="centered")

# 側邊欄重置
with st.sidebar:
    if st.button("🔄 重新開始遊戲"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# --- 2. 遊戲階段控制 ---

# 階段 0：設定玩家名字
if st.session_state.phase == "setup":
    st.title("🎮 歡迎來到數字拔河")
    st.subheader("請先設定玩家名稱")
    
    p1_input = st.text_input("玩家 1 名字 (預設: CJ)", "CJ")
    p2_input = st.text_input("玩家 2 名字 (預設: JJ)", "JJ")
    
    if st.button("開始遊戲！"):
        st.session_state.p1_name = p1_input
        st.session_state.p2_name = p2_input
        st.session_state.current_turn_name = p1_input
        st.session_state.p1_visible_hand_for_p2 = [1, 2, 3, 4, 5, 0]
        st.session_state.phase = "play"
        st.rerun()

# 階段 A：換人遮蔽畫面
elif st.session_state.phase == "confirm":
    st.title("🪢 數字拔河")
    st.warning(f"🔒 內容已隱藏，請將手機交給 **{st.session_state.current_turn_name}**")
    if st.button(f"我是 {st.session_state.current_turn_name}，準備好了"):
        st.session_state.phase = "play"
        st.rerun()

# 階段 B：正式出牌畫面
elif st.session_state.phase == "play":
    st.title("🪢 數字拔河")
    
    # 視覺化繩子
    display_pos = (st.session_state.rope_pos + 10) / 20 
    st.subheader(f"目前繩子位置: {st.session_state.rope_pos}")
    st.progress(display_pos)
    c_p2, c_mid, c_p1 = st.columns([1, 2, 1])
    c_p2.write(f"⬅️ {st.session_state.p2_name}")
    c_p1.write(f"{st.session_state.p1_name} ➡️")
    st.divider()

    st.info(st.session_state.last_result)
    
    # 勝負判定
    is_game_over = abs(st.session_state.rope_pos) >= 10 or \
                  (not st.session_state.p1_hand and st.session_state.p1_choice is None)
    
    if is_game_over:
        winner = st.session_state.p1_name if st.session_state.rope_pos > 0 else st.session_state.p2_name
        if st.session_state.rope_pos == 0: winner = "平手"
        st.success(f"🎊 遊戲結束！贏家是：{winner}")
        st.balloons()
    else:
        # 顯示對手手牌 (鎖定邏輯)
        if st.session_state.current_turn_name == st.session_state.p1_name:
            opp_name = st.session_state.p2_name
            display_hand = st.session_state.p2_hand
        else:
            opp_name = st.session_state.p1_name
            display_hand = st.session_state.p1_visible_hand_for_p2
        
        opp_hand_str = ", ".join(["空白" if c == 0 else str(c) for c in sorted(display_hand)])
        st.markdown(f"👀 **對手 ({opp_name}) 的剩餘手牌參考：** `{opp_hand_str}`")
        
        st.write(f"### 🫵 現在輪到：{st.session_state.current_turn_name}")
        
        # 取得當前玩家手牌
        current_hand = st.session_state.p1_hand if st.session_state.current_turn_name == st.session_state.p1_name else st.session_state.p2_hand
        cols = st.columns(len(current_hand))
        
        for i, card in enumerate(current_hand):
            label = "空白" if card == 0 else str(card)
            if cols[i].button(label, key=f"btn_{st.session_state.current_turn_name}_{card}_{len(current_hand)}"):
                
                if st.session_state.current_turn_name == st.session_state.p1_name:
                    st.session_state.p1_choice = card
                    st.session_state.p1_hand.remove(card)
                    st.session_state.current_turn_name = st.session_state.p2_name
                    st.session_state.phase = "confirm"
                    st.session_state.last_result = f"{st.session_state.p1_name} 已秘密出牌！"
                else:
                    # 結算
                    p1_v = st.session_state.p1_choice
                    p2_v = card
                    st.session_state.p2_hand.remove(card)
                    
                    if p1_v == 0 or p2_v == 0:
                        res = f"結果：{st.session_state.p1_name} 出 {p1_v if p1_v!=0 else '空白'} | {st.session_state.p2_name} 出 {p2_v if p2_v!=0 else '空白'}。空白牌發動，繩子不動！"
                    else:
                        diff = p1_v - p2_v
                        st.session_state.rope_pos += diff
                        res = f"結果：{st.session_state.p1_name} 出 {p1_v} | {st.session_state.p2_name} 出 {p2_v}。繩子移動了 {abs(diff)} 格！"
                    
                    # 更新鎖定手牌
                    st.session_state.p1_visible_hand_for_p2 = list(st.session_state.p1_hand)
                    
                    st.session_state.last_result = res
                    st.session_state.current_turn_name = st.session_state.p1_name
                    st.session_state.p1_choice = None
                st.rerun()
