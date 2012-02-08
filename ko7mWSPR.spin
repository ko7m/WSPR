CON

  _CLKMODE = XTAL1 + PLL16X
  _XINFREQ = 5_000_000

  WMin         =        381        'WAITCNT-expression-overhead Minimum
  NL           =         13

  RFPin        =         27

  'WSPR standard frequencies
  'Shown are the dial frequencies plus 1500 hz to put in the middle of the 200 hz WSPR band
  WSPR500KHz   =     502_400 + 1_500    ' 500 KHz
  WSPR160M     =   1_836_600 + 1_500    ' 160 metres
  WSPR80M      =   3_592_600 + 1_500    '  80 metres
  WSPR60M      =   5_287_200 + 1_500    '  60 metres
  WSPR40M      =   7_038_600 + 1_500    '  40 metres
  WSPR30M      =  10_138_700 + 1_500    '  30 metres
  WSPR20M      =  14_095_600 + 1_500    '  20 metres
  WSPR17M      =  18_104_600 + 1_500    '  17 metres
  WSPR15M      =  21_094_600 + 1_500    '  15 metres
  WSPR12M      =  24_924_600 + 1_500    '  12 metres
  WSPR10M      =  28_124_600 + 1_500    '  10 metres
  WSPR6M       =  50_293_000 + 1_500    '   6 metres
  WSPR4M       =  70_028_600 + 1_500    '   4 metres
  WSPR2M       = 144_489_000 + 1_500    '   2 metres
                      
  Frequency    =     WSPR30M
  ErrorOffset  =          20

  symbolLength =         683     ' 8192 / 12000 * 1000 = milliseconds
  TXPercent    =        0.20     ' Transmit 20% of the time or about every 10 minutes

OBJ
  Freq : "Synth"
  WSPR : "ko7mWSPREncode"
  
VAR
    LONG SecondCnt, Stack[16]
    LONG Sync
    LONG Rnd
    LONG sym                    ' Returned address of symbols to send
    BYTE interval

DAT
  myWSPRMsg byte "KO7M CN87 27", 0
               
PUB Main | iSym
  doInitialize
  repeat
    repeat iSym from 0 to 161
      sendSymbol(byte[sym][iSym]) 
    noTone
    Sync := nextSync
    repeat while SecondCnt // Sync
      delay(100)   

PUB doInitialize
  Rnd  := 22041956                     ' Initialize random number seed
  interval := 1                        ' Random time slot next
  SecondCnt := 0                       ' Set clock to zero seconds                      
  cognew(Clock, @Stack)                ' Start the clock COG
  sym := WSPR.encodeWSPR(@myWSPRMsg)
  
PUB sendCode(stringptr)
  if TXPercent > 0                     ' TXPercent of zero indicates we are not transmitting                        
    repeat strsize(stringptr)
      sendSymbol(byte[stringptr++])

PUB sendSymbol(char)
  case char
   "0", 0:
    sendTone(-3)
    delay(symbolLength)

   "1", 1:
    sendTone(-1)
    delay(symbolLength)
   "2", 2:
    sendTone(1)
    delay(symbolLength)
   "3", 3:
    sendTone(3)
    delay(SymbolLength)   

PUB sendTone(tone)
  Freq.Synth("A",RFPin, Frequency + tone + ErrorOffset)

PUB noTone
  Freq.Synth("A",RFPin, 0)

PUB delay(Duration)
  waitcnt(((clkfreq / 1_000 * Duration - 3932) #> WMin) + cnt)

PUB Clock                      ' Runs In its own COG
  repeat
    delay(1000)                ' Update second counter every 1000 ms
    SecondCnt++                ' Should be good for 2^32 seconds or about 136 years

PUB nextSync : s
  s := ROUND(1.0 / TXPercent * 2.0)    ' Calculate when next transmission occurs in minutes
  'if interval++ & 1
  '  s := (||?Rnd // s) + 1             ' Randomize the result 
  s += (s // 2)                        ' Make sure we always send on a 2 minute boundary
  s *= 60                              ' Convert minutes to seconds
  