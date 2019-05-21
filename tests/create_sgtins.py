import random
import click


@click.command()
@click.option('--count', '-c', default=1)
@click.option('--length', '-l', default=12)
@click.option('--company_prefix', '-p')
@click.option('--item_ref', '-r')
@click.option('--indicator_digit', '-i', default=0)
def main(count: int, length: int, company_prefix: str, item_ref: str, indicator_digit: int):
    click.echo(count)
    click.echo(create_sgtins(count, length, company_prefix, item_ref, indicator_digit))

def generate_alphanumeric(length: int):
    ret_val = ""
    ignore=['!','@','#','%','^','~','`','&','*','(',')','_','-','=','+',',','<','>','/','?',':',';','"','\'','[','{',']','}','\\','}','|']
    khar = ''
    i = 1
    while i <= length:
        x = random.randint(48, 125)
        if x < 33: continue
        if x > 122: continue
        if str(chr(x)) in ignore: continue
        khar = str(chr(x))
        i += 1
        ret_val += khar

    return str(ret_val).upper()


def create_sgtins(number: int, length: int, company_prefix: str, item_ref: str, indicator_digit: int=0):
    # create serial numbers
    nums = []
    sns = []

    for x in range(number):
        serial_number = generate_alphanumeric(length)
        if serial_number in sns:
            while True:
                serial_number = generate_alphanumeric(length)
                if serial_number not in sns:
                    break
        sns.append(serial_number)
        sgtin = "<epc>urn:epc:id:sgtin:{0}.{1}{2}.{3}</epc>".format(
            company_prefix,
            indicator_digit,
            item_ref,
            serial_number
        )

        nums.append(sgtin)

    return '\r\n'.join(nums)


if __name__ == "__main__":
    main()
