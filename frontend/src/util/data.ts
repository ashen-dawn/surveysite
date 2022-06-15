export type UserData = AuthenticatedUserData | AnonymousUserData;

export interface AuthenticatedUserData {
  authenticated: true;
  username: string;
  profilePictureUrl: string;
  isStaff: boolean;
}

export interface AnonymousUserData {
  authenticated: false;
  authenticationUrl: string;
}

export interface ImageData {
  name: string;
  urlSmall: string;
  urlMedium: string;
  urlLarge: string;
}

export enum Gender {
  MALE = 'M',
  FEMALE = 'F',
  OTHER = 'O',
}

export enum AnimeNameType {
  JAPANESE_NAME = 'JP',
  ENGLISH_NAME  = 'EN',
  SHORT_NAME    = 'SH',
}

export enum AnimeSeason {
  WINTER = 0,
  SPRING = 1,
  SUMMER = 2,
  FALL   = 3,
}

export enum AnimeType {
  TV_SERIES    = 'TV',
  ONA_SERIES   = 'ONAS',
  BULK_RELEASE = 'BULK',
  MOVIE        = 'MV',
  ONA          = 'ONA',
  OVA          = 'OVA',
  TV_SPECIAL   = 'TVSP',
}

export interface AnimeNameData {
  name: string;
  isOfficial: boolean;
  type: AnimeNameType;
}

export interface AnimeData {
  id: number;
  names: AnimeNameData[];
  images: ImageData[];
  animeType: AnimeType;
}

export interface SurveyData {
  year: number;
  season: AnimeSeason;
  isPreseason: boolean;
  openingEpochTime: number;
  closingEpochTime: number;
}

export enum ResultType {
  POPULARITY                  =  1,
  POPULARITY_MALE             =  2,
  POPULARITY_FEMALE           =  3,
  GENDER_POPULARITY_RATIO     =  4,
  SCORE                       = 11,
  SCORE_MALE                  = 12,
  SCORE_FEMALE                = 13,
  GENDER_SCORE_DIFFERENCE     = 14,
  UNDERWATCHED                = 21,
  SURPRISE                    = 22,
  DISAPPOINTMENT              = 23,
  AGE                         = 24,
}

// eslint-disable-next-line @typescript-eslint/no-empty-interface
export interface ValidationErrorData extends Record<string, ValidationErrorData | string[] | undefined> { }

export interface SelectorItem {
  id: number;
  name: string;
}