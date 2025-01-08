# Desmos Mathquill Parser
A Python CLI script used to convert markdown-like syntax into Mathquill that
can be pasted into Desmos' UI.

## Installation
First, clone the repository:
```git clone https://github.com/Itsskiip/desmos-mathquill-parser.git```

The `rply` python library is used to help parse input. You can install it with:
```pip install rply```

Finally, run the script from the command line:
```py mathquill.py -h```

## Usage
The script accepts 3 forms of input.

### In-line Input (Default)
```
>> py mathquill.py "#+ Parse this text"

\class{dcg-displaysize-large}{Parse\ this\ text}
```

```
>> py mathquill.py "#- Text can span
>> multiple lines
>> #+ **!!!**"

\class{dcg-search-container}{\mathit{#\ Lines\ can\ span}\mathit{multiple\ li‌nes}}\class{dcg-displaysize-large}\mathbf{!!!}
```

### Interactive Input
```
>> py mathquill.py -i                  
>> Type \end to compile or \exit to leave >> **Bold Text!**
>> Type \end to compile or \exit to leave >> \end

\mathbf{Bold\ Text!}

>> Type \end to compile or \exit to leave >> *Italics!*   
>> Type \end to compile or \exit to leave >> \end

\mathit{Italics!}

>> Type \end to compile or \exit to leave >> \exit
```

### File Input

sample.txt
```
Parse this chunk of text!

\next

Also, parse this
chunk of text!
```

CLI
```
>> py mathquill.py -f sample.txt

Parse\ this\ chunk\ o\mathrm{\mathit{‌f‌}}\ text!
\class{dcg-search-container}{\mathit{Also,\ parse\ this}}\mathit{chunk\ o\mathrm{\mathit{‌f‌}}\ text!}

>> py mathquill.py -f sample.txt -x 0

Parse\ this\ chunk\ o\mathrm{\mathit{‌f‌}}\ text!
```