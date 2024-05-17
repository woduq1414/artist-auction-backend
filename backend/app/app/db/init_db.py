from app.schemas.artist_schema import IArtistCreate
from app.schemas.account_schema import IAccountCreate
from sqlmodel.ext.asyncio.session import AsyncSession
from app import crud
from app.schemas.common_schema import ILoginTypeEnum, IGenderEnum, IAccountTypeEnum
from app.schemas.role_schema import IRoleCreate
from app.core.config import settings
from app.schemas.user_schema import IUserCreate
from app.schemas.team_schema import ITeamCreate
from app.schemas.hero_schema import IHeroCreate
from app.schemas.group_schema import IGroupCreate
from datetime import datetime


artists: list[IArtistCreate] = [
    IArtistCreate(
        nickname="The Artist",
        birthdate=datetime(1990, 1, 1),
        gender = IGenderEnum.male,
        favorite_category="111",
    ),
    IArtistCreate(
        nickname="jaeyeop",
        birthdate=datetime(2003, 12, 19),
        gender = IGenderEnum.male,
        favorite_category="111",
    )
]

artist_accounts: list[IAccountCreate] = [
    IAccountCreate(
        name="김민수",
        email="example@example.com",
        password="password",
        login_type=ILoginTypeEnum.password,
        account_type=IAccountTypeEnum.artist
        
    ),
    IAccountCreate(
        name="김철수",
        email="example2@example.com",
        password="password",
        login_type=ILoginTypeEnum.password,
        account_type=IAccountTypeEnum.artist
    )

]
        


# roles: list[IRoleCreate] = [
#     IRoleCreate(name="admin", description="This the Admin role"),
#     IRoleCreate(name="manager", description="Manager role"),
#     IRoleCreate(name="user", description="User role"),
# ]

# groups: list[IGroupCreate] = [
#     IGroupCreate(name="GR1", description="This is the first group")
# ]

# users: list[dict[str, str | IUserCreate]] = [
#     {
#         "data": IUserCreate(
#             name="Admin",
#             password=settings.FIRST_SUPERUSER_PASSWORD,
#             email=settings.FIRST_SUPERUSER_EMAIL,
#             is_superuser=True,
#             login_type=ILoginTypeEnum.password,
#             is_email_verified=True
#         ),
#         "role": "admin",
#     },
#     {
#         "data": IUserCreate(
#             name="Manager",
#             password=settings.FIRST_SUPERUSER_PASSWORD,
#             email="manager@example.com",
#             is_superuser=False,
#             login_type=ILoginTypeEnum.password,
#             is_email_verified=True
#         ),
#         "role": "manager",
#     },
#     {
#         "data": IUserCreate(
#             name="User",
#             password=settings.FIRST_SUPERUSER_PASSWORD,
#             email="user@example.com",
#             is_superuser=False,
#             login_type=ILoginTypeEnum.password,
#             is_email_verified=True
#         ),
#         "role": "user",
#     },
# ]

# teams: list[ITeamCreate] = [
#     ITeamCreate(name="Preventers", headquarters="Sharp Tower"),
#     ITeamCreate(name="Z-Force", headquarters="Sister Margaret's Bar"),
# ]

# heroes: list[dict[str, str | IHeroCreate]] = [
#     {
#         "data": IHeroCreate(name="Deadpond", secret_name="Dive Wilson", age=21),
#         "team": "Z-Force",
#     },
#     {
#         "data": IHeroCreate(name="Rusty-Man", secret_name="Tommy Sharp", age=48),
#         "team": "Preventers",
#     },
# ]


async def init_db(db_session: AsyncSession) -> None:
    for artist, artist_account in zip(artists, artist_accounts):
        current_artist = await crud.artist.get_artist_by_nickname(
            nickname=artist.nickname, db_session=db_session
        )
        if not current_artist:
            new_artist = await crud.artist.create(obj_in=artist, db_session=db_session)
            
            artist_account.artist_id = new_artist.id
            await crud.account.create(obj_in=artist_account, db_session=db_session)
        else:
            
            account = await crud.account.get_by_artist_id(
                artist_id=current_artist.id, db_session=db_session
            )
            if not account:
                artist_account.artist_id = current_artist.id
                await crud.account.create(obj_in=artist_account, db_session=db_session)
            
            
            
    
    
    # for role in roles:
    #     role_current = await crud.role.get_role_by_name(
    #         name=role.name, db_session=db_session
    #     )
    #     if not role_current:
    #         await crud.role.create(obj_in=role, db_session=db_session)

    # for user in users:
    #     current_user = await crud.user.get_by_email(
    #         email=user["data"].email, db_session=db_session
    #     )

    #     role = await crud.role.get_role_by_name(
    #         name=user["role"], db_session=db_session
    #     )
    #     if not current_user:
    #         user["data"].role_id = role.id
    #         await crud.user.create_with_role(obj_in=user["data"], db_session=db_session)

    # for group in groups:
    #     current_group = await crud.group.get_group_by_name(
    #         name=group.name, db_session=db_session
    #     )
    #     if not current_group:
    #         current_user = await crud.user.get_by_email(
    #             email=users[0]["data"].email, db_session=db_session
    #         )
    #         new_group = await crud.group.create(
    #             obj_in=group, created_by_id=current_user.id, db_session=db_session
    #         )
    #         current_users = []
    #         for user in users:
    #             current_users.append(
    #                 await crud.user.get_by_email(
    #                     email=user["data"].email, db_session=db_session
    #                 )
    #             )
    #         await crud.group.add_users_to_group(
    #             users=current_users, group_id=new_group.id, db_session=db_session
    #         )

    # for team in teams:
    #     current_team = await crud.team.get_team_by_name(
    #         name=team.name, db_session=db_session
    #     )
    #     if not current_team:
    #         current_user = await crud.user.get_by_email(
    #             email=users[0]["data"].email, db_session=db_session
    #         )
    #         await crud.team.create(
    #             obj_in=team, created_by_id=current_user.id, db_session=db_session
    #         )

    # for heroe in heroes:
    #     current_heroe = await crud.hero.get_heroe_by_name(
    #         name=heroe["data"].name, db_session=db_session
    #     )
    #     team = await crud.team.get_team_by_name(
    #         name=heroe["team"], db_session=db_session
    #     )
    #     if not current_heroe:
    #         current_user = await crud.user.get_by_email(
    #             email=users[0]["data"].email, db_session=db_session
    #         )
    #         new_heroe = heroe["data"]
    #         new_heroe.team_id = team.id
    #         await crud.hero.create(
    #             obj_in=new_heroe, created_by_id=current_user.id, db_session=db_session
    #         )
