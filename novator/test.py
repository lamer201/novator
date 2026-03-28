import sys


def main():
    n = int(input())
    a = list(map(int, input().split()))
    
    # Префиксные суммы
    prefix_sum = [0] * n
    prefix_sum[0] = a[0]
    for i in range(1, n):
        prefix_sum[i] = prefix_sum[i-1] + a[i]
    
    # Массив для результата
    result = [0] * n
    
    
    # Идем с конца и проверяем, может ли текущая компания поглотить всех следующих
    for i in range(n-1):
        # Если текущая компания может поглотить следующую компанию (которая может победить)
        # и сумма всех компаний до текущей включительно позволяет поглотить следующую компанию
        if a[i] + prefix_sum[i] >= a[i+1] and result[i+1] == 1:
            result[i] = 1
    
    # Выводим результат
    print('\n'.join(map(str, result)))

if __name__ == "__main__":
    main()