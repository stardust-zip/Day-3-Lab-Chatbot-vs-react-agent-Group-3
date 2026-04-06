# Flowcharts — ReAct Agent Traces

## Flowchart tong quat: ReAct Loop

```
+-------------------+
|   User Question   |
+--------+----------+
         |
         v
+--------+----------+
| Generate Thought  |<-----------+
| (LLM call)        |            |
+--------+----------+            |
         |                       |
    +----+----+                  |
    |         |                  |
    v         v                  |
 Final     Action              |
 Answer?   found?              |
    |         |                  |
    | YES     | YES              |
    v         v                  |
 +--+---+ +--+--------+         |
 |RETURN| |Execute Tool|         |
 +------+ +--+--------+         |
              |                  |
              v                  |
        +-----+-------+         |
        | Observation  +---------+
        | (tool result)|
        +-------------+

        [Loop until Final Answer or max_steps]
```

---

## Test Case 1: Tim dien thoai Samsung duoi 3 trieu

**Ket qua mong doi:** Samsung Galaxy A05: 2.490.000d

### Chatbot
```
User: "Tim giup toi dien thoai Samsung duoi 3 trieu"
  |
  v
LLM (1 call, 2478ms, 115 tokens)
  |
  v
"Co mot so mau Samsung duoi 3 trieu..."  --> BIA DAT, khong co ten/gia cu the
```

### Agent v1 (3 steps, SUCCESS)
```
User: "Tim giup toi dien thoai Samsung duoi 3 trieu"
  |
  v
Step 1: Thought: Can tim dien thoai duoi 3 trieu
        Action: search_by_price(3000000)
        Observation: Samsung Galaxy A05: 2,490,000d / Oppo A18: 2,990,000d
  |
  v
Step 2: Thought: Can loc chi Samsung
        Action: search_by_brand(Samsung)
        Observation: [5 san pham Samsung]
  |
  v
Step 3: Thought: Chi co Galaxy A05 duoi 3 trieu
        Final Answer: Samsung Galaxy A05, 2,490,000d (con 15 sp)  --> CHINH XAC
```

### Agent v2 (2 steps, SUCCESS)
```
User: "Tim giup toi dien thoai Samsung duoi 3 trieu"
  |
  v
Step 1: Thought: Tim dien thoai duoi 3 trieu
        Action: search_by_price(3000000)
        Observation: Samsung Galaxy A05: 2,490,000d / Oppo A18: 2,990,000d
  |
  v
Step 2: Final Answer: Samsung Galaxy A05 (2.490.000d)  --> CHINH XAC, IT BUOC HON v1
```

> **Nhan xet:** v2 hieu qua hon (2 buoc vs 3 buoc). Tuy nhien v2 bi hallucination nho: noi them "Galaxy M04" khong co trong kho.

---

## Test Case 2: Mua iPhone 17 Pro + op lung + kinh cuong luc + hoi khuyen mai

**Ket qua mong doi:** Tong 33.490.000d + liet ke cac khuyen mai phu hop

### Chatbot
```
User: "Mua iPhone 17 Pro + op lung + kinh cuong luc het bao nhieu, co KM gi?"
  |
  v
LLM (1 call, 1877ms, 180 tokens)
  |
  v
"Gia dao dong tuy dung luong... vui long ghe cua hang"  --> KHONG TRA LOI DUOC
```

### Agent v1 (5 steps, MAX_STEPS_EXCEEDED)
```
User: "Mua iPhone 17 Pro + op lung + kinh cuong luc, co KM gi?"
  |
  v
Step 1: Action: check_stock(iphone 17 pro)       --> 32,990,000d
Step 2: Action: check_stock(op lung iphone 17 pro) --> 350,000d
Step 3: Action: check_stock(kinh cuong luc ...)    --> 150,000d
Step 4: Action: calculator(32990000+350000+150000)  --> 33,490,000d
Step 5: Action: list_promotions(all)               --> [5 chuong trinh KM]
  |
  v
HET 5 BUOC — chua kip tra Final Answer!  --> THAT BAI (max_steps_exceeded)
```

### Agent v2 (5 steps, SUCCESS)
```
User: "Mua iPhone 17 Pro + op lung + kinh cuong luc, co KM gi?"
  |
  v
Step 1: Action: check_stock(iPhone 17 Pro)          --> 32,990,000d
Step 2: Action: check_stock(op lung iPhone 17 Pro)   --> 350,000d
Step 3: Action: check_stock(kinh cuong luc ...)      --> 150,000d
Step 4: Action: list_promotions(all)                 --> [5 KM, COMBO3 phu hop]
Step 5: Thought: COMBO3 giam 8%, MUANHIEU giam 7%
        calculator(33490000 * 0.93) --> tu tinh
        Final Answer: Tong 33.490.000d, KM "MUANHIEU" giam 7% --> 31.144.300d
        --> THANH CONG
```

> **Nhan xet:** v1 THAT BAI vi max_steps=5 khong du cho 6 hanh dong. v2 thanh cong nho max_steps=7 va xu ly thong minh hon.

---

## Test Case 3: Cua hang co ban dien thoai cua nhung hang nao?

**Ket qua mong doi:** Apple, Samsung, Xiaomi, OPPO

### Chatbot
```
User: "Cua hang co ban dien thoai cua nhung hang nao?"
  |
  v
LLM (1 call, 1359ms)
  |
  v
"Apple, Samsung, Xiaomi, Oppo, Huawei..."  --> SAI (bia them Huawei)
```

### Agent v1 (2 steps, SUCCESS)
```
Step 1: Action: list_brands(all) --> Apple(5), OPPO(2), Samsung(5), Xiaomi(2)
Step 2: Final Answer: Apple, OPPO, Samsung, Xiaomi  --> CHINH XAC
```

### Agent v2 (2 steps, SUCCESS)
```
Step 1: Action: list_brands(all) --> Apple(5), OPPO(2), Samsung(5), Xiaomi(2)
Step 2: Final Answer: Apple, OPPO, Samsung, Xiaomi  --> CHINH XAC
```

> **Nhan xet:** Chatbot BIA them Huawei. Ca 2 agent deu chinh xac, hieu qua ngang nhau.

---

## Test Case 4: Mua combo + ap dung ma HSSV2026

**Ket qua mong doi:** (32.990.000 + 350.000 + 150.000) * 0.95 = 31.815.500d

### Chatbot
```
User: "Mua iPhone 17 Pro + op lung + kinh cuong luc, KM HSSV2026?"
  |
  v
LLM (1 call, 2638ms)
  |
  v
"iPhone 17 Pro gia khoang 30 trieu... op lung 500.000d... kinh 300.000d...
 HSSV2026 giam 10%... tong 27.720.000d"
  --> SAI HOAN TOAN (bia gia, sai % giam, sai tong)
```

### Agent v1 (5 steps, MAX_STEPS_EXCEEDED)
```
Step 1: check_stock(iphone 17 pro)          --> 32,990,000d
Step 2: check_stock(op lung iphone 17 pro)   --> 350,000d
Step 3: check_stock(kinh cuong luc ...)      --> 150,000d
Step 4: get_discount(HSSV2026)               --> giam 5%
Step 5: calculator(32990000 * 0.95)          --> 31,340,500
  |
  v
HET 5 BUOC — chua kip cong op lung + kinh + Final Answer!
  --> THAT BAI (max_steps_exceeded) + TINH SAI (chi giam gia dien thoai)
```

### Agent v2 (5 steps, SUCCESS)
```
Step 1: check_stock(iPhone 17 Pro)            --> 32,990,000d
Step 2: check_stock(op lung iPhone 17 Pro)     --> 350,000d
Step 3: check_stock(kinh cuong luc ...)        --> 150,000d
Step 4: get_discount(HSSV2026)                 --> giam 5%
Step 5: calculator((32990000+350000+150000)*0.95) --> 31.815.500d
        Final Answer: Tong 33.490.000d, giam 5% = 31.815.500d
  --> CHINH XAC
```

> **Nhan xet:** Chatbot bia gia sai. Agent v1 het step. Agent v2 tinh dung nho few-shot example trong prompt.

---

## Test Case 5: Out-of-domain — Cua hang co nhan thu mua laptop khong?

**Ket qua mong doi:** Tu choi lich su, gioi thieu san pham dien thoai

### Chatbot
```
User: "Cua hang co nhan thu mua laptop khong?"
  |
  v
LLM (1 call, 945ms)
  |
  v
"Xin loi, cua hang khong thu mua laptop."  --> DUNG
```

### Agent v1 (1 step, SUCCESS)
```
Step 1: Thought: Ngoai pham vi
        Final Answer: "Cua hang chi ho tro dien thoai va phu kien"
  --> DUNG, khong goi tool nao (0 tool calls)
```

### Agent v2 (1 step, SUCCESS)
```
Step 1: Thought: Day la cau hoi ngoai pham vi
        Final Answer: "Xin loi, cua hang chi kinh doanh dien thoai va phu kien.
                       Khong nhan thu mua laptop. Quy khach co can tu van ve
                       dien thoai khong a?"
  --> DUNG, lich su hon, co cross-sell
```

> **Nhan xet:** Ca 3 deu xu ly dung. v2 tra loi chuyen nghiep nhat nho co vi du out-of-domain trong prompt.
