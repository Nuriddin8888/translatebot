from aiogram.dispatcher.filters.state import State,StatesGroup


class AdminState(StatesGroup):
    waiting_for_password = State()