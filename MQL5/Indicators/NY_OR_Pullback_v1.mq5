#property copyright "Opening Range Engine v1.0 (research, not advice)"
#property link      "https://github.com/ybagheri/opening-range-engine"
#property version   "1.00"
#property indicator_chart_window
#property indicator_buffers 8
#property indicator_plots   2

#property indicator_label1  "BUY"
#property indicator_type1   DRAW_ARROW
#property indicator_color1  clrDodgerBlue
#property indicator_width1  2
#property indicator_label2  "SELL"
#property indicator_type2   DRAW_ARROW
#property indicator_color2  clrTomato
#property indicator_width2  2

input int      InpOpeningRangeMinutes = 15;
input int      InpEMAFast             = 20;
input int      InpEMASlow             = 50;
input int      InpATRPeriod           = 14;
input double   InpMinOR_ATR           = 0.25;
input double   InpMaxOR_ATR           = 1.00;
input double   InpMaxBreakoutExt_ATR  = 0.50;
input double   InpPullbackLower_ATR   = 0.25;
input double   InpPullbackUpper_ATR   = 0.10;
input double   InpMinStop_ATR         = 0.10;
input double   InpMaxStop_ATR         = 1.00;
input string   InpTradeStartNY        = "09:45";
input string   InpTradeEndNY          = "11:30";
input int      InpMaxTradesPerDay     = 2;
input double   InpTP_R                = 1.5;
input bool     InpShowPanel           = true;

double g_buy[];
double g_sell[];
double g_orHigh[];
double g_orLow[];
double g_entry[];
double g_sl[];
double g_tp[];
double g_state[];

int g_hEmaFast = INVALID_HANDLE;
int g_hEmaSlow = INVALID_HANDLE;
int g_hATR     = INVALID_HANDLE;

string NoTradeReason(int code)
{
   switch(code)
   {
      case 0:  return "OK";
      case 1:  return "Neutral M15 bias";
      case 2:  return "Opening Range too large";
      case 3:  return "Opening Range too small";
      case 4:  return "Opening Range incomplete (missing bars)";
      case 5:  return "Breakout occurred after trading window";
      case 6:  return "Breakout extension too large";
      case 7:  return "Pullback invalidated";
      case 8:  return "Stop distance too large";
      case 9:  return "Stop distance too small";
      case 10: return "Daily trade limit reached";
      case 11: return "Signal not confirmed before window close";
      case 12: return "Same-direction setup already active";
      case 13: return "Daily loss limit reached";
      case 14: return "Insufficient data";
   }
   return "Insufficient data";
}

string StateName(int s)
{
   switch(s)
   {
      case 0:  return "WAITING";
      case 1:  return "BULLISH_BIAS";
      case 2:  return "BEARISH_BIAS";
      case 3:  return "OR_FORMING";
      case 4:  return "OR_VALID";
      case 5:  return "BREAKOUT_DETECTED";
      case 6:  return "WAITING_PULLBACK";
      case 7:  return "PULLBACK_CONFIRMED";
      case 8:  return "SIGNAL_CONFIRMED";
      case 9:  return "TRADE_ACTIVE";
      case 10: return "SETUP_INVALIDATED";
      case 11: return "NO_TRADE";
   }
   return "WAITING";
}
int SundayOf(datetime d)
{
   MqlDateTime st;
   TimeToStruct(d, st);
   return st.day_of_week;
}

datetime SecondSundayMarch(int year)
{
   datetime d0 = StringToTime(StringFormat("%d.03.01 00:00", year));
   int firstSunday = 1 + ((7 - SundayOf(d0)) % 7);
   return StringToTime(StringFormat("%d.03.%02d 07:00", year, firstSunday + 7));
}

datetime FirstSundayNovember(int year)
{
   datetime d0 = StringToTime(StringFormat("%d.11.01 00:00", year));
   int firstSunday = 1 + ((7 - SundayOf(d0)) % 7);
   return StringToTime(StringFormat("%d.11.%02d 06:00", year, firstSunday));
}

bool IsNYDST(datetime utcTime)
{
   MqlDateTime st;
   TimeToStruct(utcTime, st);
   return (utcTime >= SecondSundayMarch(st.year)
           && utcTime < FirstSundayNovember(st.year));
}

datetime ToNewYork(datetime utcTime)
{
   return utcTime + (IsNYDST(utcTime) ? -4 * 3600 : -5 * 3600);
}

int OnInit()
{
   SetIndexBuffer(0, g_buy, INDICATOR_DATA);
   SetIndexBuffer(1, g_sell, INDICATOR_DATA);
   SetIndexBuffer(2, g_orHigh, INDICATOR_CALCULATIONS);
   SetIndexBuffer(3, g_orLow, INDICATOR_CALCULATIONS);
   SetIndexBuffer(4, g_entry, INDICATOR_CALCULATIONS);
   SetIndexBuffer(5, g_sl, INDICATOR_CALCULATIONS);
   SetIndexBuffer(6, g_tp, INDICATOR_CALCULATIONS);
   SetIndexBuffer(7, g_state, INDICATOR_CALCULATIONS);
   PlotIndexSetInteger(0, PLOT_ARROW, 233);
   PlotIndexSetInteger(1, PLOT_ARROW, 234);
   ArraySetAsSeries(g_buy, true);
   ArraySetAsSeries(g_sell, true);
   g_hEmaFast = iMA(_Symbol, PERIOD_M15, InpEMAFast, 0, MODE_EMA, PRICE_CLOSE);
   g_hEmaSlow = iMA(_Symbol, PERIOD_M15, InpEMASlow, 0, MODE_EMA, PRICE_CLOSE);
   g_hATR = iATR(_Symbol, PERIOD_M5, InpATRPeriod);
   if(g_hEmaFast == INVALID_HANDLE || g_hEmaSlow == INVALID_HANDLE
      || g_hATR == INVALID_HANDLE)
      return INIT_FAILED;
   IndicatorSetString(INDICATOR_SHORTNAME, "NY_OR_Pullback_v1");
   return INIT_SUCCEEDED;
}

int OnCalculate(const int rates_total, const int prev_calculated,
                const datetime &time[], const double &open[],
                const double &high[], const double &low[],
                const double &close[], const long &tick_volume[],
                const long &volume[], const int &spread[])
{
   if(rates_total < InpEMASlow + 5)
      return 0;
   int start = MathMax(prev_calculated - 1, 1);
   for(int i = start; i < rates_total; i++)
   {
      g_buy[i] = EMPTY_VALUE;
      g_sell[i] = EMPTY_VALUE;
      g_state[i] = 0;
   }
   return rates_total;
}

void OnDeinit(const int reason)
{
   IndicatorRelease(g_hEmaFast);
   IndicatorRelease(g_hEmaSlow);
   IndicatorRelease(g_hATR);
}

