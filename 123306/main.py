from login import Login
from bookTicket import BookTicket

if __name__ == '__main__':
    login = Login()
    login.userLogin()
    book = BookTicket()
    book.bookTickets('温忠健')