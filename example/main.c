#include <avr/io.h>
#include <stdbool.h>
#include <stdint.h>
#include <util/delay.h>

void usart_init(const uint32_t baud_rate) {
    const uint32_t ubbr = F_CPU / (16 * baud_rate) - 1;
    UBRR0H = (uint8_t)(ubbr >> 8);
    UBRR0L = (uint8_t)ubbr;

    UCSR0B = (1 << RXEN0) | (1 << TXEN0);

    // 8 bit data with 1 stop bit
    UCSR0C = (1 << UCSZ00) | (1 << UCSZ01);
}

void usart_transmit(const uint8_t data) {
    while (!(UCSR0A & (1 << UDRE0))) {}

    UDR0 = data;
}

void usart_transmit_string(const char *string) {

    while (*string != '\0') {
        usart_transmit(*string);
        string++;
    }
}

int main(void) {

    usart_init(9600);

    while (1) {
        usart_transmit_string("Hello\r\n");
        _delay_ms(2000);
    }
}
