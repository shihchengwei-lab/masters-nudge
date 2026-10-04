# 模型啟動基礎設施失敗

官方npm CLI 0.158.0-alpha.2.1在前兩個Actor請求均被服務端拒絕Sol模型，尚未開始解題、修改檔案或呼叫Provider。流程自動停止，12題工作樹已還原。這兩份原始result保留，但不作模型契約完成率樣本；固定驗收所見未改動基底不代表模型解題失敗。

目前桌面版0.159.2以Sol及Astra medium各作一次無工具READY啟動檢查，兩次exit0並正常回覆。原始events及receipt見startup-probes。下一步等待使用者對執行版本差異的選擇，不重抽任何已完成解題交付。
