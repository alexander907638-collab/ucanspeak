import type { createAuthRepository } from '~/repository/auth'
import type { createLessonsRepository } from "~/repository/lessons";
import type { createTrainerRepository } from "~/repository/trainer";
import type { createSchoolRepository } from "~/repository/schoolschool";

export type AuthRepository = ReturnType<typeof createAuthRepository>
export type LessonsRepository = ReturnType<typeof createLessonsRepository>
export type TrainerRepository = ReturnType<typeof createTrainerRepository>
export type SchoolRepository = ReturnType<typeof createSchoolRepository>


export interface IApi {
    auth: AuthRepository
    lessons: LessonsRepository
    trainer: TrainerRepository
    createSchoolRepository: SchoolRepository
}