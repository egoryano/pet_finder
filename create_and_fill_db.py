import pandas as pd
from models import db, Animal
from datetime import datetime


def fill_db():
    df = pd.read_excel('dataset.xlsx', skiprows=1, index_col=0)
    df_cols = [
        'карточка учета животного №', 'вид ', 'возраст, год', 'вес, кг',
        'кличка', 'пол', 'порода', 'окрас', 'шерсть', 'уши', 'адрес приюта',
        'дата поступления в приют', 'Социализировано (да/нет)'
    ]
    df = df[df_cols]
    df['дата поступления в приют'] = pd.to_datetime(df['дата поступления в приют'], errors='coerce')
    df = df.dropna()

    for _, row in df.iterrows():
        a = Animal(
            name=row['кличка'],
            card=row['карточка учета животного №'],
            animal=row['вид '],
            year=row['возраст, год'],
            weight=row['вес, кг'],
            male=row['пол'],
            breed=row['порода'],
            color=row['окрас'],
            swool=row['шерсть'],
            ear=row['уши'],
            address=row['адрес приюта'],
            date=row['дата поступления в приют'],
            is_social=row['Социализировано (да/нет)']
        )
        db.session.add(a)
        db.session.commit()


if __name__ == '__main__':
    db.create_all()
    fill_db()