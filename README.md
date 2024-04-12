# 2024-Spring-HW2

Please complete the report problem below:

## Problem 1

Provide your profitable path, the amountIn, amountOut value for each swap, and your final reward (your tokenB balance).

```
path: tokenB->tokenA->tokenD->tokenC->tokenB, tokenB balance=20.129888944077443
Starts with 5 tokenB
Execution result: 5 tokenB -> 5.655321988655322 tokenA
Execution result: 5.655321988655322 tokenA -> 2.4587813170979333 tokenD
Execution result: 2.4587813170979333 tokenD -> 5.0889272933015155 tokenC
Execution result: 5.0889272933015155 tokenC -> 20.129888944077443 tokenB
```

## Problem 2

What is slippage in AMM, and how does Uniswap V2 address this issue? Please illustrate with a function as an example.
"""
滑點（Slippage）在自動化做市商（AMM）中指的是交易者希望進行交易的價格與實際成交價格之間的差異。這種差異主要是由於交易規模相對於流動性池中的資金規模過大所導致的。簡而言之，當一個大額交易對流動性池的影響較大時，它會顯著改變池中代幣的價格，從而導致交易者得到比預期更少的輸出代幣。

Uniswap V2 通過使用恆定乘積公式 x * y = k 來管理流動性池，其中 x 和 y 分別是池中兩種代幣的數量，而 k 是一個常數。這個公式確保了交易前後，池中資產的乘積保持不變。在交易過程中，加入的一種代幣的數量會增加，從而減少另一種代幣的數量，以保持 k 常數不變。這種方法可以在一定程度上限制大交易對價格的影響，減少滑點。

具體來說，Uniswap V2 還引入了一個交易費用，通常是 0.3%，這部分費用是不參與價格計算的。交易者在交換代幣時，輸入金額的一部分作為費用被扣除，然後剩餘部分用於計算輸出代幣的數量。這種機制有助於進一步抑制大規模交易引起的價格波動，從而降低滑點。

def get_amount_out(amount_in, reserve_in, reserve_out):
    """
    計算交易輸出的函數。
    :param amount_in: 輸入代幣的數量
    :param reserve_in: 輸入代幣在流動性池中的儲備量
    :param reserve_out: 輸出代幣在流動性池中的儲備量
    :return: 輸出代幣的數量
    """
    # 首先從交易額中扣除 0.3% 的費用
    amount_in_with_fee = amount_in * 997 / 1000
    numerator = amount_in_with_fee * reserve_out
    denominator = reserve_in + amount_in_with_fee
    return numerator / denominator
這個函數展示了在計算輸出代幣時如何考慮交易費用以及如何根據流動性池的現有儲備和輸入的代幣數量來確定輸出數量，以保持恆定的乘積 k。
"""

## Problem 3

Please examine the mint function in the UniswapV2Pair contract. Upon initial liquidity minting, a minimum liquidity is subtracted. What is the rationale behind this design?

"""
>In the Uniswap V2 protocol, the mint function plays a critical role in managing liquidity by allowing liquidity providers to add liquidity to a pool and in return, receive liquidity tokens that represent their share of the pool. When liquidity is initially added to a new Uniswap V2 pair contract, a special mechanism is employed where a certain minimum amount of liquidity tokens, specifically 1,000 tokens, is permanently locked in the contract. This is done for several reasons:

1. **Avoiding Zero-Value Tokens**: At the very start of a liquidity pool, when the initial amounts of the two tokens are deposited, the product \( x \times y = k \) (where \( x \) and \( y \) are the reserves of the two tokens) is established for the first time. The initial liquidity tokens minted would mathematically be based on the square root of \( k \) minus 1,000. Without subtracting these 1,000 tokens, the first liquidity provider could theoretically remove all their liquidity immediately, potentially collapsing the pool or manipulating the initial token ratios and pricing.

2. **Establishing Initial Pool Integrity**: By locking away this minimum liquidity, Uniswap ensures that there is always some residual value in the pool. This discourages attempts to completely drain a pool through early withdrawals, which could be especially impactful in a low-liquidity environment. This is important for maintaining trust and stability in the pool’s early stages.

3. **Preventing Manipulation**: The initial liquidity acts as a buffer against price manipulation. In pools with very low liquidity, large price swings can occur with relatively small trades, which can be exploited by malicious actors. The minimum locked liquidity makes it harder to manipulate the pool's prices right after creation.

4. **Technical Simplifications**: This approach simplifies some aspects of the liquidity provision and token minting processes. By ensuring there’s always some liquidity in the pool, the protocol can avoid edge cases like divisions by zero or other mathematical anomalies that might occur in a pool devoid of any liquidity.

Here is a simplified version of what the mint function looks like and how the minimum liquidity subtraction is implemented:

solidity
function mint(address to) external returns (uint liquidity) {
    (uint112 _reserve0, uint112 _reserve1,) = getReserves(); // fetch the reserves
    uint balance0 = IERC20(token0).balanceOf(address(this));
    uint balance1 = IERC20(token1).balanceOf(address(this));
    uint amount0 = balance0.sub(_reserve0);
    uint amount1 = balance1.sub(_reserve1);

    bool feeOn = _mintFee(_reserve0, _reserve1);
    uint _totalSupply = totalSupply(); // total supply of LP tokens
    if (_totalSupply == 0) {
        liquidity = Math.sqrt(amount0.mul(amount1)).sub(MINIMUM_LIQUIDITY);
        _mint(address(0), MINIMUM_LIQUIDITY); // permanently lock the first MINIMUM_LIQUIDITY tokens
    } else {
        liquidity = Math.min(amount0.mul(_totalSupply) / _reserve0, amount1.mul(_totalSupply) / _reserve1);
    }
    require(liquidity > 0, "UniswapV2: INSUFFICIENT_LIQUIDITY_MINTED");
    _mint(to, liquidity);
    _update(balance0, balance1, _reserve0, _reserve1);
    if (feeOn) _mintFee(_reserve0, _reserve1);
    return liquidity;
}


This mechanism ensures that every new liquidity pool on Uniswap V2 starts with a reliable and manipulation-resistant foundation, providing better security and stability for all future transactions in that pool.
"""

## Problem 4

Investigate the minting function in the UniswapV2Pair contract. When depositing tokens (not for the first time), liquidity can only be obtained using a specific formula. What is the intention behind this?
"""
Uniswap V2 是一個去中心化交易平台，其核心部分是智能合約，包括 UniswapV2Pair 合約。這個合約管理著交易對中的兩種代幣，並允許用戶提供流動性，以及進行代幣交換。

在 UniswapV2Pair 合約中，當用戶想要向交易對中添加流動性時，他們需要存入兩種代幣。如果不是第一次添加流動性（即池子已經有其他流動性提供者的代幣），新增的流動性是通過一個特定公式計算的。這個公式基本上保證了存入代幣的比例與池子現有的比例一致。

具體來說，當您存入兩種代幣（記為 token A 和 token B）時，新增的流動性代幣（LP 代幣）的數量，是根據以下公式確定的：

\[ \text{新增 LP 代幣} = \text{存入的代幣 A 數量} \times \frac{\text{已有的 LP 代幣總量}}{\text{池中的代幣 A 總量}} \]

或者用 token B 來計算也可以，公式是一樣的結構。這樣做的目的是保持池中兩種代幣的比例不變。這種機制的設計意圖包括：

1. **價格穩定性**：通過要求用戶按照現有池子的比例存入代幣，幫助維持交易對代幣價格的穩定性。如果存入的比例不對，可能會立即影響到池中代幣的價格平衡。

2. **防止滑點**：確保當大量交易發生時，價格不會因為大量的買入或賣出而發生劇烈波動。

3. **公平性**：通過這種方式可以確保所有流動性提供者都按照公平的比例獲得流動性代幣，而不會因為市場條件的快速變化而使早期或晚期的提供者處於不利地位。

總之，這種計算方法通過維護池中代幣比例的一致性，來保護流動性提供者的利益，同時也維護了交易環境的穩定和高效。
"""

## Problem 5

What is a sandwich attack, and how might it impact you when initiating a swap?
"""
在去中心化金融（DeFi）領域中，「三明治攻擊」是一種常見的交易操縱策略，尤其是在自動化做市商（AMM）如 Uniswap 等平台上發生。這種攻擊通常針對大額交易，當交易者試圖執行這種交易時，攻擊者會利用這一機會進行市場操縱。

具體操作如下：首先，攻擊者會監測交易池，尋找即將發生的大額交易。一旦發現這種交易，他們會在目標交易之前迅速進行一筆購買，推高該代幣的價格。當目標交易執行時，由於價格已被人為抬高，交易者不得不以更高的價格購入代幣，從而獲得的代幣量會少於預期。隨後，攻擊者再執行一個賣出交易，利用高價位賣出剛才購入的代幣，從而實現利潤。

這種攻擊對普通交易者造成的直接影響包括成本增加、交易滑點加大和資產損失。由於在高於市場價格的情況下完成交易，交易者支付的成本超過了正常水平，且因代幣量的減少導致資產損失。

為了防範三明治攻擊，交易者可以通過設定較低的滑點容忍度或將大額交易拆分為多個小額交易來降低風險。然而，在當前的AMM架構中，完全避免這種攻擊仍然是一個挑戰。通过这些策略虽不能完全防范，但至少可以在一定程度上降低被攻擊的可能性和潜在的财务损失。
"""