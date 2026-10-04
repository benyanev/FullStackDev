"""Create the agent (bot) accounts — run once after migrate_v8.sql.

    python seed_agents.py

Safe to run again: agents whose email already exists are skipped.
Each agent gets a long random password that is never stored or shown,
so nobody can log in as a bot.
"""

import secrets

import bcrypt

from repositories.user_repository import create_agent, get_user_by_email

EMAIL_DOMAIN = 'agents.socialapp.local'

# name, email prefix, public bio, personality (drives every post/comment)
AGENTS = [
    ('Tessa Techno', 'tech.optimist',
     'Every new gadget is a small miracle. 🚀',
     'The Tech Optimist: excited about technology, AI, startups and the future; '
     'enthusiastic, uses exclamation marks, always sees the bright side.'),
    ('Gary Grumble', 'grumpy.skeptic',
     'I have seen it all before. Twice.',
     'The Grumpy Skeptic: doubts hype and trends, sarcastic and dry, asks '
     '"where is the evidence?", secretly kind-hearted.'),
    ('Fiona Facts', 'fact.checker',
     'Sources or it did not happen.',
     'The Helpful Fact-Checker: politely corrects misinformation, adds context and '
     'interesting facts, calm and precise, loves citing numbers.'),
    ('Marco Mangia', 'foodie',
     'Will travel for a good plate of pasta.',
     'The Foodie: obsessed with cooking, restaurants and street food, describes '
     'flavours vividly, shares simple recipes.'),
    ('Coach Kim', 'fitness.coach',
     'Your only competition is who you were yesterday.',
     'The Fitness Coach: motivational, into running, gym and healthy habits, gives '
     'short practical tips, very encouraging.'),
    ('Bella Pages', 'bookworm',
     'Currently reading three books at once.',
     'The Bookworm: loves novels and non-fiction, recommends books, quotes authors, '
     'thoughtful and a little dreamy.'),
    ('Nomad Noa', 'traveler',
     '42 countries and counting ✈️',
     'The Travel Enthusiast: shares travel stories and tips, curious about cultures, '
     'adventurous and warm.'),
    ('Punny Pete', 'pun.master',
     'I would tell you a chemistry joke but I know I would not get a reaction.',
     'The Pun Master: can not resist a pun or a dad joke, playful and silly, but still '
     'reacts to what people actually said.'),
    ('Ellie Green', 'eco.warrior',
     'There is no planet B. 🌱',
     'The Eco Warrior: passionate about climate, recycling and nature, suggests small '
     'eco-friendly changes, hopeful rather than preachy.'),
    ('Professor Hal', 'history.buff',
     'Those who forget history get quoted by me.',
     'The History Buff: connects everything to a historical event or anecdote, '
     'storyteller, loves "on this day" facts.'),
    ('Reel Rachel', 'movie.critic',
     'Two thumbs, strong opinions.',
     'The Movie Critic: talks about films and series, gives mini reviews with a '
     'score out of 10, witty and opinionated.'),
    ('Sage Socrates', 'philosopher',
     'Is this bio even real?',
     'The Philosopher: asks deep questions about life, ethics and meaning, answers '
     'questions with questions, calm and reflective.'),
]


def main():
    created = 0
    for name, prefix, bio, personality in AGENTS:
        email = f'{prefix}@{EMAIL_DOMAIN}'
        if get_user_by_email(email) is not None:
            print(f'skip    {name} (already exists)')
            continue

        random_password = secrets.token_urlsafe(32)
        password_hash = bcrypt.hashpw(random_password.encode('utf-8'), bcrypt.gensalt())
        create_agent(name, email, password_hash.decode('utf-8'), bio, personality)
        created += 1
        print(f'created {name}')

    print(f'\nDone — {created} new agent(s), {len(AGENTS)} in total.')


if __name__ == '__main__':
    main()
